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
		escaped_key = self.escape_key(key)
		value = ""
		if escaped_key in self.items:
			value = self.items[escaped_key]
		else:
			print("couldn't find " + escaped_key + " in cache")
		return value 

	def escape_key(self, key):
		p = re.compile("[^a-zA-Z0-9.\-_]")
		new_key = p.sub("_", key)
		return new_key

	def get_value_from_key_filename(self, key):
		p = re.compile(".*_value-")
		value = p.sub("", key)
		value = value.replace(".cachefile", "")
		return value

	def get_key_from_key_filename(self, key):
		p = re.compile("__value.*")
		key = p.sub("", key)
		return key