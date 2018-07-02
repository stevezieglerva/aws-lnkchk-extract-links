import boto3
import requests
from urllib.parse import *
from bs4 import BeautifulSoup
import json
from datetime import datetime
from cache import *
from ESLambdaLog import *
import sys


def lambda_handler(event, context):
    try:
        print("In lambda_handler " + str(datetime.now()))
        print("Event:")
        print(json.dumps(event))
        cache = Cache()
        db = boto3.resource("dynamodb")
        queue = db.Table("lnkchk-queue")

        ESlog = ESLambdaLog("aws_lnkchk_queue")	
        EScache = ESLambdaLog("aws_lnkchk_cache")	

        print("Number of records: " + str(len(event["Records"]) ))
        count = 0
        for record in event["Records"]:
            count = count + 1
            url_to_process = record["dynamodb"]["Keys"]["url"]["S"]

            creation_date_str = ""
            if "ApproximateCreationDateTime" in record["dynamodb"]:
                creation_epoch = record["dynamodb"]["ApproximateCreationDateTime"]
                creation_date = datetime.fromtimestamp(creation_epoch)
                creation_date_str = str(creation_date)
            timestamp = ""
            source = ""
            if "NewImage" in record["dynamodb"]:   
                if "timestamp" in record["dynamodb"]["NewImage"]:
                    timestamp = record["dynamodb"]["NewImage"]["timestamp"]["S"]
                if "source" in record["dynamodb"]["NewImage"]:
                    source = record["dynamodb"]["NewImage"]["source"]["S"]
           
            print("Processing record: "+ str(count) + ". for " + url_to_process)
            print("\tCreated: " + creation_date_str)
            print("\tTimestamp: " + timestamp)
            print("\tSource: " + source)

            event = { "event" : "process_lambda_queue", "url" : url_to_process, "created" : creation_date_str, "source" : source}
            ESlog.log_event(event)

            if record["eventName"] == "INSERT":
                print("\tRecord is INSERT")
                # Read the page
                html = download_page(url_to_process)
                links = {}
                links = extract_links(html, url_to_process)

                # Add relative links to the queue
                for key, value in links.items():
                    if value["link_location"] == "relative":
                        result = cache.get_item(key)
                        if result == "":
                            try:
                                print("\tAdding relative link: " + str(value))
                                queue.put_item(Item = {"url": key, "source" : "lambda execution", "timestamp" : str(datetime.now())})

                                event = { "event" : "add_relative_link", "url" : key, "created" : str(datetime.now()), "source" : "lambda execution"}
                                EScache.log_event(event)  
                            except UnicodeEncodeError:
                                print("\tCan't print unicode chars")
                        else:
                            print("\tRelative link " + key + "already in cache with: '" + result + "'")

                # Check the links
                for key, value in links.items(): 
                    url = key
                    link_text = value
                    if not is_link_valid(url, cache):
                        print("*** Link failed: " + url)
                print("Removing " + url_to_process + " from the queue")        
                queue.delete_item(Key = {"url" : url_to_process})
            else:
                print("\tSkipping because record is: " + record["eventName"])
    except Exception as e:
        print("Exception:")
        print(e)
        raise



def download_page(url):
    html = ""
    response = requests.get(url)
    html = response.text
    if response.status_code != 200:
        print("*** Initial lnkchk page " + url + " returned: " + response.status_code)
    return html

def extract_links(html, base_url):
    links = {}
    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.find_all('a')
    count = 0
    for link in anchors:
        count = count + 1
        url = link.get('href')
        formated_url = format_url(url, base_url)
        if url is not None:
            print("\t" + str(count) + ". " + url + " -> " + formated_url)
            if formated_url != "":
                link_location = get_link_location(url, base_url)
                links[formated_url] = {"url" :  formated_url, "link_text" : link.text, "link_location" : link_location} 
    return links

def format_url(url, base_url):
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
        print("\tChecked: " + url + " - Status: " + str(response.status_code))
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
