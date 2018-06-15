import unittest
import boto3
from cache import *


class TestMethods(unittest.TestCase):
	def test_constructor__valid_argument__object_created(self):
		# Arrange
		
		# Act
		subject = Cache("lnkchk")

		# Assert
		self.assertEqual(subject.location, "lnkchk")


	def test_add_item__existing_item__item_returned(self):
		# Arrange
		subject = Cache("lnkchk")
		subject.add_item("http://nerdthoughts.net/about.html", "200")

		# Act
		result = subject.get_item("http://nerdthoughts.net/about.html")

		# Assert
		self.assertEqual(result, "200")


	def test_get_item__existing_item__item_returned(self):
		# Arrange
		self.db = boto3.resource("dynamodb")
		cache = self.db.Table("lnkchk-cache")
		cache.put_item(Item = {"url": "http://ziegler.com", "http_result" : "200"})
		subject = Cache("lnkchk")

		# Act
		result = subject.get_item("http://ziegler.com")

		# Assert
		self.assertEqual(result, "200")


	def test_add_item__complicated_url__item_returned(self):
		# Arrange
		subject = Cache("lnkchk")
		subject.add_item("http://nerdthoughts.net/about.html?text=388292%20", "400")

		# Act
		result = subject.get_item("http://nerdthoughts.net/about.html?text=388292%20")

		# Assert
		self.assertEqual(result, "400")







if __name__ == '__main__':
	unittest.main()		


