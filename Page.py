import requests
import logging
import datetime
import json
import logging
import structlog
import traceback
from bs4 import BeautifulSoup
from Link import *


class Page():
	def __init__(self, url, html=""):
		self.url = url
		self.link = Link(self.url)
		self.response_code = 0
		if html == "":
			self.html_page = False
			self.download_sec = 0.0
			self.html = ""
			self.download()
		else:
			self.html_page = True
			self.download_sec = 0.0
			self.html = html
		if self.html_page:
			self.extracted_links = self.__extract_links()

	def __str__(self):
		page_json = {"url" : self.url, "response_code" : self.response_code, "html_page" : self.html_page, "download_sec" : self.download_sec}
		page_json = {}
		page_json["url"] = self.url
		page_json["response_code"] = self.response_code
		page_json["html_length"] = str(len(self.html)) 
		page_json["download_sec"] = self.download_sec
		page_json["extracted_links"] = self.extracted_links
		return json.dumps(page_json, sort_keys=True)

	def download(self):
		if self.avoid_downloading_slow_non_html_page():
			start = datetime.datetime.now()
			response = requests.get(self.url, timeout=30)
			end = datetime.datetime.now()
			elapsed = end - start

			self.download_sec = elapsed.total_seconds()
			self.html = response.text
			self.response_code = response.status_code
			self.html_page = True
		else:
			self.html_page = False


	def avoid_downloading_slow_non_html_page(self):
		return self.is_url_an_html_page()


	def is_url_an_html_page(self):
		response = requests.head(self.url, allow_redirects=True)
		if "Content-Type" in response.headers:
			if "text/html" in response.headers["Content-Type"]:
				return True
		return False


	def __extract_links(self):
		try:
			log = structlog.get_logger()
			log.info("__extracting_links", base_url=self.url)			
			links = {}
			soup = BeautifulSoup(self.html, "html.parser")
			anchors = soup.find_all('a')
			count = 0

			for href in anchors:
				count = count + 1
				url = href.get("href")
				log.info("got_href", url=url)
				if url is None:
					# Link has no href and is placeholder for future frontend processing
					continue
				try:
					link = Link(url, self.url, href.text)
					formatted_url = link.url_qualified
					log.info("got_link", formatted_url=formatted_url)
					if url is not None:
						if link.url_qualified != "":
							link_location = ""
							if link.is_external_link:
								link_location = "external"
							else:
								link_location = "relative"
							#links[formatted_url] = {"url" :  formatted_url, "link_text" : href.text, "link_location" : link_location} 
							link_json = link.toJSON()
							links[formatted_url] = link_json
				except Exception as e:
					exception_name = type(e).__name__
					log.exception("formatting_url_exception", exception_name=exception_name, formatted_url=formatted_url)
					traceback.print_exc()
					continue
		except Exception as e:
			exception_name = type(e).__name__
			log.exception("basic_extract_url_exception", exception_name=exception_name)
			traceback.print_exc()
		return links

