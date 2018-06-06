import boto3
import requests
from bs4 import BeautifulSoup


def lambda_handler(event, context):
    print("In lambda_handler ...")

    sqs = boto3.resource('sqs')

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName="lnkchk-pages")

    # Process messages by printing out body and optional author name
    for message in queue.receive_messages(MessageAttributeNames=["file", "line"]):
        # Get the custom author message attribute if it was set
        file_attribute = ""
        if message.message_attributes is not None:
            file_name = message.message_attributes.get("file").get("StringValue")
            if file_name:
                file_attribute = ' ({0})'.format(file_name)

        url_to_process = message.body
        print("\tFound queue message:, {0}!{1}".format(url_to_process, file_attribute))

        html = download_page(url_to_process)
        links = {}
        links = extract_links(html, url_to_process)

        # Let the queue know that the message is processed
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
    for link in anchors:
        print(link.get('href'))
        links[link.get('href')] = link.text 
    return links

def format_url(url, base_url):
    return url

