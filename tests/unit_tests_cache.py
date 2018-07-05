import unittest
import boto3
from cache import *


class TestMethods(unittest.TestCase):
	def test_constructor__valid_argument__object_created(self):
		# Arrange
		
		# Act
		subject = Cache()

		# Assert
		self.assertEqual(subject.location, "lnkchk-cache")


	def test_add_item__existing_item__item_returned(self):
		# Arrange
		subject = Cache("lnkchk-cache")
		subject.add_item("http://nerdthoughts.net/about.html", "200")

		# Act
		result = subject.get_item("http://nerdthoughts.net/about.html")

		# Assert
		self.assertEqual(result, "200")


	def test_add_item__complicated_url__item_returned(self):
		# Arrange
		subject = Cache("lnkchk-cache")
		subject.add_item("http://nerdthoughts.net/about.html?text=388292%20", "400")

		# Act
		result = subject.get_item("http://nerdthoughts.net/about.html?text=388292%20")

		# Assert
		self.assertEqual(result, "400")


	def test_clear__cache_with_items__cache_is_empty(self):
		# Arrange
		subject = Cache("lnkchk-cache")
		subject.add_item("http://shouldbe.empty", "500")

		# Act
		subject.clear()
		result = subject.get_item("http://shouldbe.empty")

		# Assert
		self.assertEqual(result, "")




if __name__ == '__main__':
	unittest.main()		


