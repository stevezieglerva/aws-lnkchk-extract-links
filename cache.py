import boto3
import re
import json
from datetime import datetime

class Cache:
	def __init__(self, location = "lnkchk-cache"):
		self.location = location

		print("Reading cache from " + self.location)
		self.db = boto3.resource("dynamodb")
		self.cache = self.db.Table(self.location)
		self.items = {}

## 		Too slow for 1,000s of items. Populate on get_item instead
##		response = self.cache.scan()
##		for item in response["Items"]:
##			url = item["url"]
##			http_result = item["http_result"]
##			self.items[url] = http_result

	def add_item(self, key, value):
		self.items[key] = value
		self.cache.put_item(Item = {"url": key, "http_result" : str(value), "timestamp" : str(datetime.now())})

	def get_item(self, key):
		value = ""
		if key in self.items:
			value = self.items[key]
		else:
			item = self.cache.get_item(Key={"url" : key})	
			if "http_result" in item:
				value = item["http_result"]
				self.items[key] = item["http_result"]
		return value 

	def clear(self):
		for key in self.items.keys():
			self.cache.delete_item(Key = {"url" : key})
		self.items.clear()
		
 