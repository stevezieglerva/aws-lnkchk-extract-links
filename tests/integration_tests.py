import unittest
from lambda_function import *
import boto3
from datetime import datetime


class TestMethods(unittest.TestCase):
	def test_aws_lnkchk_extract_links__file_payload_espn__lambda_called(self):
		# Arrange
		payload = ""
		with open("..\\test_payload_nerdthoughts.json", "r") as f:
			payload = f.read()
			f.close()
		event = json.loads(payload)
		cache = Cache()
		cache.clear()

		# Act
		print("Calling lambda_handler ...")
		lambda_handler(event, "")

		# Assert


	def test_aws_lnkchk_extract_links__only_add_item_to_table__logs_updated(self):
		# Arrange
		db = boto3.resource("dynamodb")
		queue = db.Table("lnkchk-queue")
		queue.put_item(Item = {"url": "http://nerdthoughts.net", "source" : "integration test only_add_item_to_table", "timestamp" : str(datetime.now())})

		# Act

		# Assert

if __name__ == '__main__':
	unittest.main()		


