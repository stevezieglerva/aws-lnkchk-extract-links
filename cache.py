import boto3
import re
import json

class Cache:
	def __init__(self, location):
		self.location = location
		self.s3 = boto3.resource('s3')
		self.bucket = self.s3.Bucket(location)

		print("Reading cache")
		self.db = boto3.resource("dynamodb")
		cache = self.db.Table("lnkchk-cache")
		response = cache.scan()

		self.items = {}
		for item in response["Items"]:
			url = item["url"]
			http_result = item["http_result"]
			self.items[url] = http_result
			print(url + ": " + str(http_result))



	def add_item(self, key, value):
		escaped_key = self.escape_key(key)
		s3_filename = escaped_key + "__value-" + value + ".cachefile"
		obj = self.bucket.put_object(Key=s3_filename)
		self.items[escaped_key] = value
		return obj

	def get_item(self, key):
		value = ""
		if key in self.items:
			value = self.items[key]
		else:
			print("couldn't find " + key + " in cache")
		return value 

