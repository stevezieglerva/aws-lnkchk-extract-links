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
		result = extract_links(html, "http://www.example.com")

		# Assert
		self.assertEqual(len(result), 1)
		self.assertEqual(result["http://www.cnn.com"]["link_text"], "Click here")
		self.assertEqual(result["http://www.cnn.com"]["link_location"], "external")


	def test_extract_links__relative_links__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'>Click here</a>   <a href='/'>Return to home page</a>  <a href='/subpage/test.html'>Test</a>  </html>"

		# Act
		result = extract_links(html, "http://www.example.com")

		# Assert
		self.assertEqual(len(result), 3)
		self.assertEqual(result["http://www.cnn.com"]["link_text"], "Click here")
		self.assertEqual(result["http://www.cnn.com"]["link_location"], "external")
		self.assertEqual(result["http://www.example.com/"]["link_text"], "Return to home page")
		self.assertEqual(result["http://www.example.com/"]["link_location"], "relative")
		self.assertEqual(result["http://www.example.com/subpage/test.html"]["link_text"], "Test")
		self.assertEqual(result["http://www.example.com/subpage/test.html"]["link_location"], "relative")



	def test_check_link_location__relative_link__relative_link_found(self):
		# Arrange

		# Act
		result = get_link_location("/subpage/test.html", "http://www.example.com") 

		# Assert
		self.assertEqual(result, "relative")

	def test_check_link_location__same_site_link__relative_link_found(self):
		# Arrange

		# Act
		result = get_link_location("http://www.example.com/subpage/test.html", "http://www.example.com") 

		# Assert
		self.assertEqual(result, "relative")

	def test_check_link_location__external_link__external_link_found(self):
		# Arrange

		# Act
		result = get_link_location("https://www.cnn.com", "http://www.example.com") 

		# Assert
		self.assertEqual(result, "external")

	def test_check_link_location__same_site_with_https__relative_link_found(self):
		# Arrange

		# Act
		result = get_link_location("http://www.example.com/subpage/test.html", "https://www.example.com") 

		# Assert
		self.assertEqual(result, "relative")

	def test_extract_links__several_links__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'>Click here for CNN</a><a href='http://www.google.com'>Click here for Google</a></html>"

		# Act
		result = extract_links(html, "http://www.example.com")

		# Assert
		self.assertEqual(len(result), 2)
		self.assertEqual(result["http://www.cnn.com"]["link_text"], "Click here for CNN")
		self.assertEqual(result["http://www.google.com"]["link_text"], "Click here for Google")
		

	def test_extract_links__no_link_text__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'/></html>"

		# Act
		result = extract_links(html, "http://www.example.com")

		# Assert
		self.assertEqual(len(result), 1)
		self.assertEqual(result["http://www.cnn.com"]["link_text"], "")


	def test_extract_links__https_link__returns_links(self):
		# Arrange
		html = "<html><a href='https://www.cnn.com'>Click here</a></html>"

		# Act
		result = extract_links(html, "http://www.example.com")

		# Assert
		self.assertEqual(len(result), 1)
		self.assertEqual(result["https://www.cnn.com"]["link_text"], "Click here")


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


