import boto3
import requests
from urllib.parse import *
from bs4 import BeautifulSoup
import json
import datetime
import time
from cache import *
from ESLambdaLog import *
from LocalTime import *
from LinkCheckResult import *
from Page import *
from Link import *
import sys
import os
import traceback
import logging
import structlog


def lambda_handler(event, context):
    try:
        local_time = LocalTime()
        #log_level = get_environment_variable("log_level", "INFO")
        log = setup_logging()
        
        if context != "":
            log = log.bind(request_id=context.aws_request_id)

        if not event.get("async"):
            log.critical("05_starting_sync", timestamp_local = str(local_time.local), version= 19 ) 
            invoke_self_async(event, context)
            lambda_results = {"pages_processed" : -1, "links_checked" : -1}
            return lambda_results


        log.critical("10_starting_async", timestamp_local = str(local_time.local)) 
        log.critical("15_input_event", input_event=event)
        
        short_circuit_pattern = get_environment_variable("url_short_circuit_pattern", "")
        include_url_pattern = get_environment_variable("include_url_pattern", "")

        log.critical("16_environment_variables", short_circuit=short_circuit_pattern, include_pattern=include_url_pattern)
        link_check_result = LinkCheckResult()

        cache = Cache()
        db = boto3.resource("dynamodb")
        queue = db.Table("lnkchk-queue")
        results = db.Table("lnkchk-results")

        log.critical("17_number_of_records", num_records=len(event["Records"]))
        count = 0
        for record in event["Records"]:
            try:
                if  record["eventName"] != "INSERT":
                    log.warning("21_skipping", reason="Not an insert record")
                    continue

                count = count + 1
                url_to_process = record["dynamodb"]["Keys"]["url"]["S"]
                url_to_process = url_to_process.strip()

                creation_date_str = ""
                if "ApproximateCreationDateTime" in record["dynamodb"]:
                    creation_epoch = record["dynamodb"]["ApproximateCreationDateTime"]
                    creation_date = datetime.datetime.fromtimestamp(creation_epoch)
                    creation_date_str = str(creation_date)
                timestamp = ""
                source = ""
                if "NewImage" in record["dynamodb"]:   
                    if "timestamp" in record["dynamodb"]["NewImage"]:
                        timestamp = record["dynamodb"]["NewImage"]["timestamp"]["S"]
                    if "source" in record["dynamodb"]["NewImage"]:
                        source = record["dynamodb"]["NewImage"]["source"]["S"]
                log = log.bind(main_page_url=url_to_process)
                log = log.bind(source=source)
 
                if "\r" in url_to_process:
                    log.warning("skipping", reason="url has carriage return")
                    continue

                if continue_to_process_link(short_circuit_pattern, include_url_pattern, url_to_process):
                    if record["eventName"] == "INSERT":
                        log.critical("20_processing_record", number=count)
                        link_check_result.pages_processed = link_check_result.pages_processed + 1

                        # Read the page
                        current_page = Page(url_to_process)
                        html = current_page.html
                        log.warning("30_downloaded_page", page_size=len(html))
                        links = {}
                        links = current_page.extracted_links
                        log.warning("40_extracted_links", link_count=len(links))

                        # Add relative links to the queue
                        for link in links:
                            url = link["url_qualified"]
                            internal_page = not link["is_link_external"]
                            if internal_page:
                                result = cache.get_item(url)
                                if result == "":
                                    try:
                                        if is_url_an_html_page(url) and matches_include_pattern(include_url_pattern, url):
                                            log.warning("50_adding_relative_links", new_link=url)
                                            local_time.now()
                                            queue.put_item(Item = {"url": url, "source" : "lambda execution", "timestamp" : str(local_time.utc), "timestamp_local" : str(local_time.local)})
                                    except UnicodeEncodeError:
                                        log.error("52_exception_adding_relative_links", new_link=url)
                                else:
                                    log.warning("55_relative_link_already_in_cache")

                        # Check the links
                        for link in links: 
                            url = link["url_qualified"]
                            link_text = link["link_text"]

                            check the link
                            if not is_link_valid(url, cache):
                                log.warning("65_found_broken_link", broken_link=url)
                                local_time.now()
                                broken_link = {"broken_link" : url, "page_url" : url_to_process, "link_text" : value["link_text"], "timestamp" : str(local_time.utc), "timestamp_local" : str(local_time.local) }
                                results.put_item(Item = broken_link)
                            link_check_result.links_checked = link_check_result.links_checked + 1
                            log.warning("66_checked_link", checked_link=url)                            
                    else:
                        log.warning("25_skipping_not_insert")
                else:
                    log.warning("26_skipping_short_circuit_or_include")
            except Exception as e:
                exception_name = type(e).__name__
                log.exception("27b_skipping_exception", exception_name=exception_name, reason="exception during processing")
            log.info("70_removing_link_from_queue")
            queue.delete_item(Key = {"url" : url_to_process})  
            log = log.unbind("main_page_url")
            log = log.unbind("source")            
    except Exception as e:
        log.exception("75_breaking_exception", reason="stopping all processing")        
        raise
    log.critical("80_finished", timestamp_local = str(local_time.local), finished_pages_processed=link_check_result.pages_processed, finished_links_checked=link_check_result.links_checked) 
    lambda_results = {"pages_processed" : link_check_result.pages_processed, "links_checked" : link_check_result.links_checked}
    return lambda_results


def invoke_self_async(event, context):
    log = structlog.get_logger()
    event["async"] = True
    log.warning("06_invoke_self_async", context=context)
    boto3.client("lambda").invoke(
        FunctionName="aws-lnkchk-extract-links",
        InvocationType='Event',
        Payload=bytes(json.dumps(event), "utf-8")
        )


def setup_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()


def get_environment_variable(variable_name, default):
        variable_value = ""
        if variable_name in os.environ:
            variable_value = os.environ[variable_name]
        else:    
            variable_value = default
        return variable_value

def continue_to_process_link(short_circuit_pattern, include_url_pattern, url):
    short_circuit = need_to_short_circuit_url(short_circuit_pattern, url) 
    matches_include = matches_include_pattern(include_url_pattern, url)
    return ((not short_circuit) and matches_include)

def need_to_short_circuit_url(short_circuit_pattern, url):
    short_circuit = False
    if short_circuit_pattern != "":
        m = re.search(short_circuit_pattern, url)
        if m:
            short_circuit = True
    return short_circuit

def matches_include_pattern(include_url_pattern, url):
    include = False
    if include_url_pattern != "":
        m = re.search(include_url_pattern, url)
        if m:
            include = True
    else:
        include = True
    return include

def download_page(url, cache):
    html = ""
    if is_url_an_html_page(url):
        response = requests.get(url, timeout=30)
        html = response.text
        if response.status_code != 200:
            print("*** Initial lnkchk page " + url + " returned: " + str(response.status_code))
            cache.add_item(url, response.status_code)
    else:
        print("*** Page is not HTML Content-Type")
    return html

def is_url_an_html_page(url):
    response = requests.head(url, allow_redirects=True)
    if "Content-Type" in response.headers:
        if "text/html" in response.headers["Content-Type"]:
            return True
    return False

def extract_links(html, base_url):
    try:
        log = structlog.get_logger()
        links = {}
        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.find_all('a')
        count = 0

        for link in anchors:
            count = count + 1
            url = link.get('href')
            if url is None:
                # Link has no href and is placeholder for future frontend processing
                continue
            try:
                formatted_url = format_url(url, base_url)
                if url is not None:
                    if formatted_url != "":
                        link_location = get_link_location(url, base_url)
                        links[formatted_url] = {"url" :  formatted_url, "link_text" : link.text, "link_location" : link_location} 
            except Exception as e:
                exception_name = type(e).__name__
                log.exception("62_formatting_url_exception", exception_name=exception_name, formatted_url=formatted_url)
                continue
    except Exception as e:
        exception_name = type(e).__name__
        log.exception("63_basic_extract_url_exception", exception_name=exception_name)
    return links

def format_url(url, base_url):
    try:
        if "mailto:" in url:
            return ""
        if is_relative_path(url):
            path = get_url_path(url)
            if is_anchor_link(path):
                url = ""
            else:
                first_char = path[0]
                if is_anchor_link(path):
                    return ""
                base_url_parts = urlsplit(base_url)
                seperator = "/"
                if first_char == "/":
                    seperator = ""
                url = base_url_parts.scheme + "://" + base_url_parts.netloc + seperator + url
        elif is_missing_scheme(url):
            url = "http:" + url 
    except:
        print("Exception in format_url")
        traceback.print_exc()
    return url

def is_anchor_link(path):
    if path == "":
        return True
    else:
        return False

def is_relative_path(url):
    url_parts = urlsplit(url)
    if url_parts.scheme == "" and url_parts.netloc == "": 
        return True
    else:
        return False

def is_missing_scheme(url):
    url_parts = urlsplit(url)
    if url_parts.scheme == "" and url_parts.netloc != "": 
        return True
    else:
        return False

def get_url_path(url):
    url_parts = urlsplit(url)
    return url_parts.path

def is_link_valid(url, cache):
    log = structlog.get_logger()
    cached_result = cache.get_item(url)
    log.warning("61a_is_link_valid", result_cache=cached_result)
    if cached_result == "":
        response = requests.head(url, timeout=30)
        log = structlog.get_logger()
        log.info("checked_link", url=url, status=response.status_code)
        # HEAD requests not allowed
        if response.status_code == 405:
            print("\t HEAD not allowed so trying GET on: " + url)
            response = requests.get(url, timeout=30)
            print("\t\tChecked: " + url + " - Status: " + str(response.status_code))
        cache.add_item(url, response.status_code)
        if response.status_code < 400:
            log.warning("65a_broken_link_response", status_code=response.status_code)
            return True
        else:
            return False
    else:
        print("\tCache hit: " + url + " = " + str(cached_result))
        if int(cached_result) >= 400:
            return False
        else:
            return True



def get_link_location(url, base_url):
    link_location = "external"
    if is_relative_path(url):
        link_location = "relative"

    url_parts = urlsplit(url)
    base_url_parts = urlsplit(base_url)
    if url_parts.netloc == base_url_parts.netloc:
        link_location = "relative"    

    return link_location
