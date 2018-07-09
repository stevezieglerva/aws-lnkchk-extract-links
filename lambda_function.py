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
import sys
import os
import traceback
import logging
import structlog


def lambda_handler(event, context):
    try:
        local_time = LocalTime()
        log_level = get_environment_variable("log_level", "WARNING")

 
                        
        log = structlog.get_logger()
        log.critical("starting", timestamp_local = str(local_time.local)) 
        log.critical("input_event", input_event=event)

        
        short_circuit_pattern = get_environment_variable("url_short_circuit_pattern", "")
        include_url_pattern = get_environment_variable("include_url_pattern", "")

        log.critical("environment_variables", short_circuit=short_circuit_pattern, include_pattern=include_url_pattern)
        link_check_result = LinkCheckResult()

        cache = Cache()
        db = boto3.resource("dynamodb")
        queue = db.Table("lnkchk-queue")
        results = db.Table("lnkchk-results")

        log.critical("number_of_records", num_records=len(event["Records"]))
        count = 0
        for record in event["Records"]:
            try:
                if  record["eventName"] != "INSERT":
                    log.warning("Skipping since not a queue INSERT Event")
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
                log = log.bind(url=url_to_process)
                log = log.bind(source=source)
                log.critical("processing_record", number=count)

                if "\r" in url_to_process:
                    print("Skipping leftover nerdthoughts with carriage return")
                    continue

                if continue_to_process_link(short_circuit_pattern, include_url_pattern, url_to_process):
                    if record["eventName"] == "INSERT":
                        link_check_result.pages_processed = link_check_result.pages_processed + 1

                        # Read the page
                        html = download_page(url_to_process)
                        log.warning("downloaded_page", page_size=len(html))
                        links = {}
                        links = extract_links(html, url_to_process)
                        log.warning("extracted_links", link_count=len(links))

                        # Add relative links to the queue
                        log.warning("adding_relative_links")
                        for key, value in links.items():
                            if value["link_location"] == "relative":
                                result = cache.get_item(key)
                                if result == "":
                                    try:
                                        if is_url_an_html_page(key) and matches_include_pattern(include_url_pattern, key):
                                            print("\tAdding relative link: " + str(value))
                                            local_time.now()
                                            queue.put_item(Item = {"url": key, "source" : "lambda execution", "timestamp" : str(local_time.utc), "timestamp_local" : str(local_time.local)})

                                            event = { "event" : "add_relative_link", "url" : key, "created" : local_time.now(), "source" : "lambda execution"}
                                    except UnicodeEncodeError:
                                        print("\tCan't print unicode chars")
                                else:
                                    print("\tRelative link " + key + "already in cache with: '" + result + "'")

                        # Check the links
                        print("\t\tChecking the links")
                        for key, value in links.items(): 
                            url = key
                            link_text = value
                            if not is_link_valid(url, cache):
                                print("*** Link failed: " + url)
                                local_time.now()
                                broken_link = {"broken_link" : url, "page_url" : url_to_process, "link_text" : value["link_text"], "timestamp" : str(local_time.utc), "timestamp_local" : str(local_time.local) }
                                results.put_item(Item = broken_link)
                            link_check_result.links_checked = link_check_result.links_checked + 1
                        print("Removing " + url_to_process + " from the queue")
                    else:
                        print("Skipping due to short circuit url: " + url_to_process)        
                else:
                    print("\tSkipping because record is: " + record["eventName"])
            except Exception as e:
                print("ERROR Exception in Records loop: " + str(e))
                print("Skipping and removing " + url_to_process + " from the because of the exception error")        
            queue.delete_item(Key = {"url" : url_to_process})              
    except Exception as e:
        print("ERROR Exception outside or Records loop:" + str(e))
        raise
    log.critical("finished", timestamp_local = str(local_time.local)) 
    lambda_results = {"pages_processed" : link_check_result.pages_processed, "links_checked" : link_check_result.links_checked}
    return lambda_results


def setup_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.WARNING,
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
        p = re.compile(short_circuit_pattern)
        m = p.match(url)
        if m:
            short_circuit = True
    return short_circuit

def matches_include_pattern(include_url_pattern, url):
    include = False
    if include_url_pattern != "":
        p = re.compile(include_url_pattern)
        m = p.match(url)
        if m:
            include = True
    else:
        include = True
    return include

def download_page(url):
    html = ""
    if is_url_an_html_page(url):
        response = requests.get(url)
        html = response.text
        if response.status_code != 200:
            print("*** Initial lnkchk page " + url + " returned: " + str(response.status_code))
        return html
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
        links = {}
        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.find_all('a')
        count = 0

        for link in anchors:
            count = count + 1
            url = link.get('href')
            if url is None:
                print("Link has no href")
                continue
            try:
                formated_url = format_url(url, base_url)
                if url is not None:
                    print("\t" + str(count) + ". " + url + " -> " + formated_url)
                    if formated_url != "":
                        link_location = get_link_location(url, base_url)
                        links[formated_url] = {"url" :  formated_url, "link_text" : link.text, "link_location" : link_location} 
            except Exception as e:
                print("Exception while extracting link #" + str(count) + " for: " + formated_url )
                traceback.print_exc()
                continue
    except Exception as e:
        print("Exception in initial extract_links logic :" + str(e))
        traceback.print_exc()
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
    cached_result = cache.get_item(url)
    if cached_result == "":
        response = requests.head(url)
        print("\t\tChecked: " + url + " - Status: " + str(response.status_code))
        # HEAD requests not allowed
        if response.status_code == 405:
            print("\t HEAD not allowed so trying GET on: " + url)
            response = requests.get(url)
            print("\t\tChecked: " + url + " - Status: " + str(response.status_code))
        cache.add_item(url, response.status_code)
        if response.status_code < 400:
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
