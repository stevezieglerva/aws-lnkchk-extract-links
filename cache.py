import boto3
import re
import json
import datetime
from LocalTime import *

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
		local_time = LocalTime()
		ttl_seconds = 5
		self.cache.put_item(Item = {"url": key, "http_result" : str(value), "timestamp" : str(local_time.utc), "timestamp_local" : str(local_time.local), "ttl_epoch": local_time.get_epoch_plus_seconds(ttl_seconds) })

	def get_item(self, key):
		print("Cache - getting " + key)
		value = ""
		if key in self.items:
			print("Cache - In local cache")
			value = self.items[key]
		else:
			item = self.cache.get_item(Key={"url" : key})	
			print("Cache - table item:")
			if "Item" in item:
				if "http_result" in item["Item"]:
					print("Cache - In table cache")
					value = item["Item"]["http_result"]
					self.items[key] = value
		return value 

	def clear(self):
		for key in self.items.keys():
			self.cache.delete_item(Key = {"url" : key})
		self.items.clear()
		



 