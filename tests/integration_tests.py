import unittest
from lambda_function import *
import boto3
from datetime import datetime
import os

class TestMethods(unittest.TestCase):
##	def test_aws_lnkchk_extract_links__file_payload_espn__lambda_called(self):
##		# Arrange
##		payload = ""
##		with open("..\\test_payload_nerdthoughts.json", "r") as f:
##			payload = f.read()
##			f.close()
##		event = json.loads(payload)
##
##		db = boto3.resource("dynamodb")
##		queue = db.Table("lnkchk-queue")
##		response = queue.scan()
##		for item in response["Items"]:self
##			url = item["url"]
##			queue.delete_item(Key = {"url" : url})
##
##		cache = Cache()
##		cache.clear()
##
##		# Act
##		print("Calling lambda_handler ...")
##		lambda_handler(event, "")
##
##		# Assert


##	def test_aws_lnkchk_extract_links__only_add_item_to_table__logs_updated(self):
##		# Arrange
##		db = boto3.resource("dynamodb")
##		queue = db.Table("lnkchk-queue")
##		response = queue.scan()
##
##		for item in response["Items"]:
##			url = item["url"]
##			queue.delete_item(Key = {"url" : url})
##		cache = Cache()
##		cache.clear()
##
##		# Act
##		queue.put_item(Item = {"url": "http://lnkchk-simple-site-integration.s3-website-us-east-1.amazonaws.com/", "source" : "integration test only_add_item_to_table", "timestamp" : str(datetime.now())})
##
##		# Assert


##	def test_aws_lnkchk_extract_links__only_add_item_to_table_complex__logs_updated(self):
##		# Arrange
##		db = boto3.resource("dynamodb")
##		queue = db.Table("lnkchk-queue")
##
##		cache = Cache()
##		cache.clear()
##
##		# Act
##		queue.put_item(Item = {"url": "http://lnkchk-complex-site-integration.s3-website-us-east-1.amazonaws.com/", "source" : "integration test only_add_item_to_table", "timestamp" : str(datetime.now())})
##
##		# Assert


	def test_aws_lnkchk_extract_links__short_circuit_link__no_pages_checked(self):
		# Arrange
		payload = ""
		with open("..\\test_payload_short_circuit.json", "r") as f:
			payload = f.read()
			f.close()
		event = json.loads(payload)

		db = boto3.resource("dynamodb")
		queue = db.Table("lnkchk-queue")
		response = queue.scan()
		for item in response["Items"]:
			url = item["url"]
			queue.delete_item(Key = {"url" : url})

		cache = Cache()
		cache.clear()

		os.environ["url_short_circuit_pattern"] = ".*steveziegler.*"

		# Act
		print("Calling lambda_handler ...")
		result = lambda_handler(event, "")

		# Assert
		self.assertEqual(result["pages_processed"], 0)
		self.assertEqual(result["links_checked"], 0)
		

	def test_aws_lnkchk_extract_links__simple_site__pages_checked(self):
		# Arrange
		payload = ""
		with open("..\\test_payload_simple.json", "r") as f:
			payload = f.read()
			f.close()
		event = json.loads(payload)

		db = boto3.resource("dynamodb")
		queue = db.Table("lnkchk-queue")
		response = queue.scan()
		for item in response["Items"]:
			url = item["url"]
			queue.delete_item(Key = {"url" : url})

		cache = Cache()
		cache.clear()

		# Act
		print("Calling lambda_handler ...")
		result = lambda_handler(event, "")

		# Assert
		self.assertEqual(result["pages_processed"], 1)
		self.assertEqual(result["links_checked"], 2)

	def test_aws_lnkchk_extract_links__complex_site__pages_checked(self):
		# Arrange
		payload = ""
		with open("..\\test_payload_complex.json", "r") as f:
			payload = f.read()
			f.close()
		event = json.loads(payload)

		db = boto3.resource("dynamodb")
		queue = db.Table("lnkchk-queue")
		response = queue.scan()
		for item in response["Items"]:
			url = item["url"]
			queue.delete_item(Key = {"url" : url})

		cache = Cache()
		cache.clear()

		# Act
		print("Calling lambda_handler ...")
		result = lambda_handler(event, "")

		# Assert
		self.assertEqual(result["pages_processed"], 1)
		self.assertEqual(result["links_checked"], 3)



if __name__ == '__main__':
	unittest.main()		



