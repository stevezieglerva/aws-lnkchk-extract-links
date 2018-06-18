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

if __name__ == '__main__':
	unittest.main()		


