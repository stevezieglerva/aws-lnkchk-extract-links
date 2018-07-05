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
##		response = self.cache.scan()
##
		self.items = {}
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
		return value 

	def clear(self):
		for key in self.items.keys():
			self.cache.delete_item(Key = {"url" : key})
		self.items.clear()
		
 