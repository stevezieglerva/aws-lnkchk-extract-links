import requests
import logging
import datetime
import json


class Page():
	def __init__(self, url):
		self.url = url
		self.response_code = 0
		self.html = ""
		self.extract_links = {}
		self.html_page = False
		self.download_sec = 0.0

		self.download()

	def __str__(self):
		page_json = {"url" : self.url, "response_code" : self.response_code, "html_page" : self.html_page, "download_sec" : self.download_sec}
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



