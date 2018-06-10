import boto3
import requests
from urllib.parse import *
from bs4 import BeautifulSoup
import json
from datetime import datetime


def lambda_handler(event, context):
    print("In lambda_handler ...")

    sqs = boto3.client('sqs')

    # Get messages from the queue
    queue_url = "https://queue.amazonaws.com/112280397275/lnkchk-pages"

    response = sqs.receive_message(QueueUrl=queue_url, MessageAttributeNames=["file", "line"], MaxNumberOfMessages=5)
    print(json.dumps(response, indent=4, sort_keys=False))
    if "Messages" in response:
        messages = response["Messages"]
        print("Found: " + str(len(messages)))
        for message in messages:
            file_attribute = ""
            if message["MessageAttributes"] is not None:
                file_name = message["MessageAttributes"]["file"]["StringValue"]
                if file_name:
                    file_attribute = ' ({0})'.format(file_name)

            url_to_process = message["Body"]
            print("\tFound queue message:, {0} {1}".format(url_to_process, file_attribute))

            # Read the page
            html = download_page(url_to_process)
            links = {}
            links = extract_links(html, url_to_process)
            print("Found links:")
            print(json.dumps(links, indent=4, sort_keys=False))


            # Add relative links to the queue
            for key, value in links.items():
                if value["link_location"] == "relative":
                    print("Adding relative link: ")
                    print(str(value))
##                    response = sqs.send_message(QueueUrl=queue_url, DelaySeconds=10, MessageBody=value["url"],  MessageAttributes={
##                        'file': {
##                            'DataType': 'String',
##                            'StringValue': 'Lambda run at ' + str(datetime.now())
##                        },
##                        'line': {
##                            'DataType': 'String',
##                            'StringValue': 'no line number'
##                        },
##                        'source': {
##                            'DataType': 'String',
##                            'StringValue': 'Lambda run at ' + str(datetime.now())
##                        }
##                        })

            # Check the links
            for key, value in links.items(): 
                url = key
                link_text = value
                if not is_link_valid(url):
                    print("*** Link failed: " + url)

            receipt_handle = message["ReceiptHandle"]
            result = sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle )
            print("Deleted: " + str(result))


def download_page(url):
    html = ""
    response = requests.get(url)
    html = response.text
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
            seperator = "/"
            if first_char == "/":
                seperator = ""
            url = base_url + seperator + url
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

def is_link_valid(url):
    response = requests.head(url)
    print("\t\tChecked: " + url + " - Status: " + str(response.status_code))
    if response.status_code < 400:
        return True
    else:
        return False

def get_link_location(url, base_url):
    link_location = "external"
    if is_relative_path(url):
        link_location = "relative"

    url_parts = urlsplit(url)
    base_url_parts = urlsplit(base_url)
    if url_parts.netloc == base_url_parts.netloc:
        link_location = "relative"    

    return link_location
