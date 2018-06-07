import unittest
from lambda_function import *


class TestMethods(unittest.TestCase):
	def test_download_page__valid_url__html_download(self):
		# Arrange

		# Act
		html = download_page("https://www.cnn.com")

		# Assert
		assert "html" in html.lower(), "Expected page html to be returned"

	def test_download_page__redirect_url__html_download(self):
		# Arrange

		# Act
		html = download_page("http://cnn.com")

		# Assert
		assert "html" in html.lower(), "Expected page html to be returned"

	def test_download_page__bad_url__error_thrown(self):
		# Assert
		with self.assertRaises(Exception) as context:
			download_page("hello.world")
		self.assertTrue('Invalid URL' in str(context.exception))


	def test_extract_links__good_html__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'>Click here</a></html>"

		# Act
		links = extract_links(html, "http://www.example.com")

		# Assert
		assert len(links) ==  1, "Expected to find links"
		assert links["http://www.cnn.com"] == "Click here", "Expected to find links"

	def test_extract_links__several_links__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'>Click here</a><a href='http://www.google.com'>Click here for Google</a></html>"

		# Act
		links = extract_links(html, "http://www.example.com")

		# Assert
		assert len(links) == 2, "Expected to find links"
		assert links["http://www.cnn.com"] == "Click here"
		assert links["http://www.google.com"] == "Click here for Google"

	def test_extract_links__no_link_text__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'/></html>"

		# Act
		links = extract_links(html, "http://www.example.com")

		# Assert
		assert len(links) == 1, "Expected to find links"
		assert links["http://www.cnn.com"] == ""

	def test_extract_links__https_link__returns_links(self):
		# Arrange
		html = "<html><a href='https://www.cnn.com'>Click here</a></html>"

		# Act
		links = extract_links(html, "http://www.example.com")

		# Assert
		assert len(links) ==  1, "Expected to find links"
		assert links["https://www.cnn.com"] == "Click here", "Expected to find links"


	def test_format_url__full_url__no_change(self):
		# Arrange

		# Act
		test_url = "http://www.example.com"
		result = format_url(test_url, "http://www.example.com")

		# Assert
		expected = "http://www.example.com"
		self.assertEqual(result, expected)


	def test_format_url__relative_link__base_added(self):
		# Arrange

		# Act
		test_url = "/relative/page.html"
		result = format_url(test_url, "http://www.example.com")

		# Assert
		expected = "http://www.example.com/relative/page.html"
		self.assertEqual(result, expected)

	def test_format_url__relative_link_no_slash__base_added(self):
		# Arrange

		# Act
		test_url = "relative/page.html"
		result = format_url(test_url, "http://www.example.com")

		# Assert
		expected = "http://www.example.com/relative/page.html"
		self.assertEqual(result, expected)

	def test_format_url__link_with_query_strings__base_added(self):
		# Arrange

		# Act
		test_url = "/test.html?hello=world"
		result = format_url(test_url, "http://www.example.com")

		# Assert
		expected = "http://www.example.com/test.html?hello=world"
		self.assertEqual(result, expected)

	def test_format_url__pure_anchor_link__base_added(self):
		# Arrange

		# Act
		test_url = "#top"
		result = format_url(test_url, "http://www.example.com")

		# Assert
		expected = ""
		self.assertEqual(result, expected)

	def test_format_url__link_with_anchor__base_added(self):
		# Arrange

		# Act
		test_url = "http://example.com/page.html#top"
		result = format_url(test_url, "http://www.example.com")

		# Assert
		expected = "http://example.com/page.html#top"
		self.assertEqual(result, expected)

	def test_format_url__double_slash__base_added(self):
		# Arrange

		# Act
		test_url = "//store.cnn"
		result = format_url(test_url, "http://www.example.com")

		# Assert
		expected = "http://store.cnn"
		self.assertEqual(result, expected)




if __name__ == '__main__':
	unittest.main()		


