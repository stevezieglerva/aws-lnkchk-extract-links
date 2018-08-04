import unittest
from Link import *


class TestMethods(unittest.TestCase):
	def test_constructor__full_link__valid_url_parts(self):
		# Arrange
		
		# Act
		url = "http://google.com/ziegler"
		subject = Link(url)
		self.assertEqual(subject.original_url, url, "Expected url to be the same")
		self.assertEqual(subject.url_scheme, "http")
		self.assertEqual(subject.url_netloc, "google.com")
		self.assertEqual(subject.url_path, "/ziegler")
		self.assertFalse(subject.is_relative_path)

	def test_constructor__relative_link__valid_url_parts(self):
		# Arrange
		
		# Act
		url = "/parent/page.html"
		link_text = "Click here!"
		subject = Link(url, "https://example.com", link_text)
		self.assertEqual(subject.link_text, link_text, "Expected url to be the same")
		self.assertEqual(subject.original_url, url, "Expected url to be the same")
		self.assertEqual(subject.url_qualified, "https://example.com/parent/page.html", "Expected a qualified url")
		self.assertEqual(subject.url_scheme, "https")
		self.assertEqual(subject.url_netloc, "example.com")
		self.assertEqual(subject.url_path, "/parent/page.html")
		self.assertTrue(subject.is_relative_path, "Expected relative path")
		self.assertFalse(subject.is_external_link, "Did not expect external path")		

	def test_constructor__external_link__valid_url_parts(self):
		# Arrange
		
		# Act
		url = "https://www.cnn.com"
		subject = Link(url, "https://example.com")
		self.assertEqual(subject.original_url, url, "Expected url to be the same")
		self.assertEqual(subject.url_qualified, "https://www.cnn.com", "Expected a qualified url")
		self.assertEqual(subject.url_scheme, "https")
		self.assertEqual(subject.url_netloc, "www.cnn.com")
		self.assertEqual(subject.url_path, "")
		self.assertFalse(subject.is_relative_path, "Did not expect relative path")
		self.assertTrue(subject.is_external_link, "Expected external link")

	def test_constructor__local_anchor_link__empty_url_parts(self):
		# Arrange
		
		# Act
		url = "#section"
		subject = Link(url, "https://example.com")
		self.assertEqual(subject.original_url, url, "Expected url to be the same")
		self.assertEqual(subject.url_qualified, "")
		self.assertEqual(subject.url_scheme, "")
		self.assertEqual(subject.url_netloc, "")
		self.assertEqual(subject.url_path, "")

	def test_constructor__double_slash__valid_url_parts(self):
		# Arrange
		
		# Act
		url = "//store.cnn"
		subject = Link(url, "https://www.cnn.com")
		self.assertEqual(subject.original_url, url, "Expected url to be the same")
		self.assertEqual(subject.url_qualified, "https://store.cnn")
		self.assertEqual(subject.url_scheme, "https")
		self.assertEqual(subject.url_netloc, "store.cnn")
		self.assertEqual(subject.url_path, "")

	def test_constructor__string_version_of_oject__includes_braces(self):
		# Arrange
		url = "/parent/page.html"
		subject = Link(url, "https://example.com")
		
		# Act
		link_str = str(subject)
		print(link_str)

		self.assertIn("\"original_url\"", link_str)
		self.assertIn("\"is_external_link\"", link_str)

	def test_check__valid_full_url__returns_true(self):
		# Arrange
		url = "https://google.com"
		subject = Link(url, "https://google.com")
		
		# Act
		result = subject.check_if_link_is_valid()

		self.assertTrue(result, "Expectced URL to be valid")

	def test_check__valid_relative_url__returns_true(self):
		# Arrange
		url = "/world"
		subject = Link(url, "https://www.cnn.com")
		
		# Act
		result = subject.check_if_link_is_valid()

		self.assertTrue(result, "Expectced URL to be valid")

	def test_check__valid_domain_but_bad_page__returns_false(self):
		# Arrange
		url = "http://google.com/stevezieglernothere"
		subject = Link(url, "https://www.cnn.com")
		
		# Act
		result = subject.check_if_link_is_valid()

		self.assertFalse(result, "Expectced URL to be invalid")

	def test_check__invalid_domain__returns_false(self):
		# Arrange
		url = "http://invalid_domain.stevezieglernothere.com"
		subject = Link(url, "https://www.cnn.com")
		
		# Act
		result = subject.check_if_link_is_valid()

		self.assertFalse(result, "Expectced URL to be invalid")


	def test_placeholder_add_url_to_cache_after_checking_to_main(self):
		assert 1 == 0

	def test_placeholder_add_check_cache_before_to_main(self):
		assert 1 == 0


if __name__ == '__main__':
	unittest.main()		


