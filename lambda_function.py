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
                        print(json.dumps(current_page.toJSON(), indent=3))
                        log.warning("30_downloaded_page", page_size=len(current_page.html))
                        cache.add_item(current_page.url, current_page.response_code)

                        links = {}
                        links = current_page.extracted_links
                        log.warning("40_extracted_links", link_count=len(links))

                        # Add relative links to the queue
                        for link in links:
                            url = link.url_qualified
                            internal_page = not link.is_external_link
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
                            url = link.url_qualified
                            link_text = link.link_text
                            checked_link = is_link_valid(link, cache)
                            is_broken_link = not checked_link.is_link_valid
                            if is_broken_link:
                                log.warning("65_found_broken_link", broken_link=url)
                                local_time.now()
                                broken_link = {"broken_link" : url, "page_url" : url_to_process, "link_text" : link.link_text, "timestamp" : str(local_time.utc), "timestamp_local" : str(local_time.local) }
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

def is_url_an_html_page(url):
    response = requests.head(url, allow_redirects=True)
    if "Content-Type" in response.headers:
        if "text/html" in response.headers["Content-Type"]:
            return True
    return False


def is_link_valid(link, cache):
    url = link.url_qualified
    log = structlog.get_logger()
    cached_result = cache.get_item(url)
    link_valid = False
    found_in_cache = False
    if cached_result == "":
        link_valid = link.check_if_link_is_valid()
    else:
        found_in_cache = True
        if int(cached_result) <= 400:
            link_valid = True
    log.info("61_is_link_valid", url=url, link_valid=link_valid, found_in_cache=found_in_cache)
    return link


