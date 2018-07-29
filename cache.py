import boto3
import re
import json
import datetime
from LocalTime import *
import logging
import structlog

class Cache:
	def __init__(self, location = "lnkchk-cache"):
		self.location = location

		self.db = boto3.resource("dynamodb")
		self.cache = self.db.Table(self.location)
		self.items = {}

	def add_item(self, key, value):
		self.items[key] = value
		local_time = LocalTime()
		ttl_seconds = 60 * 60 * 8
		self.cache.put_item(Item = {"url": key, "http_result" : str(value), "timestamp" : str(local_time.utc), "timestamp_local" : str(local_time.local), "ttl_epoch": local_time.get_epoch_plus_seconds(ttl_seconds) })

	def get_item(self, key):
		log = structlog.get_logger()
		value = ""
		if key in self.items:
			log.info("63_cache_hit_local", url = key) 
			value = self.items[key]
		else:
			item = self.cache.get_item(Key={"url" : key})	
			if "Item" in item:
				if "http_result" in item["Item"]:
					log.info("63_cache_hit_table", url = key) 
					value = item["Item"]["http_result"]
					self.items[key] = value
				else:
					log.info("63_cache_missed", url = key) 
		return value 

	def clear(self):
		for key in self.items.keys():
			self.cache.delete_item(Key = {"url" : key})
		self.items.clear()
		



 