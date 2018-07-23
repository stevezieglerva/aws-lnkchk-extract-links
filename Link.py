import logging
import structlog
import requests
import traceback
from urllib.parse import *
import json

class Link():
	def __init__(self, url, page_of_link_url = "", link_text = ""):
		self.link_text = link_text
		self.original_url = url
		self.page_of_link_url = page_of_link_url
		self.response_code = 0
		self.url_qualified = self.__format_url()
		url_parts = urlsplit(self.url_qualified)
		self.url_scheme = url_parts.scheme
		self.url_netloc = url_parts.netloc
		self.url_path = url_parts.path
		self.is_relative_path = self.__is_relative_path()
		self.is_external_link = self.__is_external_link()
		self.is_link_valid = False

	def check_if_link_is_valid(self):
		log = structlog.get_logger()
		url = self.url_qualified
		response_status_code = 0
		try:
			response = requests.head(url, timeout=5)
			log.info("checked_link_head", url=url, status=response.status_code)
			response_status_code = response.status_code
			# if HEAD requests not allowed
			if response_status_code == 405:
				response = requests.get(url, timeout=30)
				log.info("checked_link_get", url=url, status=response_status_code)

			if response.status_code < 400:
				log.warning("link_is_valid", url=url, status_code=response.status_code)
				self.is_link_valid = True
				return True
			else:
				log.warning("link_is_broken", url=url, status_code=response.status_code)
				self.is_link_valid = False
				return False
				
		except requests.exceptions.ConnectionError as e:
			log.error("bad_domain_exception_in_link_checking", type=e.__class__.__name__)
			traceback.print_exc()
			return False

		except Exception as e:
			log.error("unknown_exception_in_link_checking", url=url, type=e.__class__.__name__)
			traceback.print_exc()	
			raise
					
	def toJSON(self):
		page_json = {}
		page_json["link_text"] = self.link_text
		page_json["original_url"] = self.original_url
		page_json["page_of_link_url"] = self.page_of_link_url
		page_json["response_code"] = self.response_code
		page_json["url_qualified"] = self.url_qualified
		page_json["url_scheme"] = self.url_scheme
		page_json["url_netloc"] = self.url_netloc
		page_json["url_path"] = self.url_path
		page_json["is_relative_path"] = str(self.is_relative_path)
		page_json["is_external_link"] = str(self.is_external_link)
		return page_json

	def __str__(self):
		page_json = self.toJSON()
		return json.dumps(page_json, sort_keys=True)		

	def __is_anchor_link(self, path):
		if path == "":
			return True
		else:
			return False

	def __is_relative_path(self):
		url_parts = urlsplit(self.original_url)
		if url_parts.scheme == "" and url_parts.netloc == "": 
			return True
		else:
			return False

	def __is_external_link(self):
		is_external = True
		if self.is_relative_path:
			is_external = False

		page_of_link_url_parts = urlsplit(self.page_of_link_url)
		if self.url_netloc == page_of_link_url_parts.netloc:
			is_external = False
		return is_external

	def __is_missing_scheme(self, url):
		url_parts = urlsplit(url)
		if url_parts.scheme == "" and url_parts.netloc != "": 
			return True
		else:
			return False

	def __format_url(self):
		try:
			url = self.original_url
			page_of_link_url = self.page_of_link_url
			if "mailto:" in url:
				return ""
			if self.__is_relative_path():
				path = urlsplit(url).path
				if self.__is_anchor_link(path):
					url = ""
				else:
					first_char = path[0]
					if self.__is_anchor_link(path):
						return ""
					page_of_link_url_parts = urlsplit(page_of_link_url)
					seperator = "/"
					if first_char == "/":
						seperator = ""
					url = page_of_link_url_parts.scheme + "://" + page_of_link_url_parts.netloc + seperator + url
			elif self.__is_missing_scheme(url):
				url = "https:" + url 
		except:
			print("Exception in format_url")
			traceback.print_exc()
		return url

