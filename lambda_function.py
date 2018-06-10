import boto3
import requests
from urllib.parse import *
from bs4 import BeautifulSoup


def lambda_handler(event, context):
    print("In lambda_handler ...")

    sqs = boto3.client('sqs')

    queue = sqs.get_queue_by_name(QueueName="lnkchk-pages")
    # Get messages from the queue
    for message in queue.receive_messages(MessageAttributeNames=["file", "line"]):
        file_attribute = ""
        if message.message_attributes is not None:
            file_name = message.message_attributes.get("file").get("StringValue")
            if file_name:
                file_attribute = ' ({0})'.format(file_name)

        url_to_process = message.body
        print("\tFound queue message:, {0}!{1}".format(url_to_process, file_attribute))

        # Read the page
        html = download_page(url_to_process)
        links = {}
        links = extract_links(html, url_to_process)

        # Add relative links to the queue

        # Check the links
        for key, value in links.items(): 
            url = key
            link_text = value
            if not is_link_valid(url):
                print("*** Link failed: " + url)

        message.delete()


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
