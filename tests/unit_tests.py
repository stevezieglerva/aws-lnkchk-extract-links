import unittest
from lambda_function import *
import time


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

	def test_format_url__relative_link_with_base_subpage__relative_added_to_netloc(self):
		# Arrange

		# Act
		test_url = "/about.html"
		result = format_url(test_url, "http://www.example.com/subpage/checkingnow.html")

		# Assert
		expected = "http://www.example.com/about.html"
		self.assertEqual(result, expected)

	def test_format_url__relative_link_with_base_subpage_and_https___relative_added_to_netloc(self):
		# Arrange

		# Act
		test_url = "/about.html"
		result = format_url(test_url, "https://www.example.com/subpage/checkingnow.html")

		# Assert
		expected = "https://www.example.com/about.html"
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


	def test_is_link_valid__valid_url__returns_true(self):
		# Arrange
		cache = Cache()

		# Act
		result = is_link_valid("http://google.com", cache)

		# Assert
		self.assertEqual(result, True)

	def test_is_link_valid__invalid_url__returns_false(self):
		# Arrange
		cache = Cache()

		# Act
		result = is_link_valid("http://nerdthoughts.net/xyz", cache)

		# Assert
		self.assertEqual(result, False)

	def test_is_link_valid__valid_url_in_cache__returns_true(self):
		# Arrange
		cache = Cache()
		cache.clear()
		cache.add_item("https://www.google.com", "200")

		# Act
		result = is_link_valid("https://www.google.com", cache)

		# Assert
		self.assertEqual(result, True)

	def test_is_link_valid__invalid_url_in_cache__returns_false(self):
		# Arrange
		cache = Cache()
		cache.clear()
		cache.add_item("http://nerdthoughts.net/xyzincache", "404")

		# Act
		result = is_link_valid("http://nerdthoughts.net/xyzincache", cache)

		# Assert
		self.assertEqual(result, False)

	def test_is_url_an_html_page__cnn_with_redirect__returns_true(self):
		# Arrange
		url = "http://www.cnn.com"

		# Act
		result = is_url_an_html_page(url)

		# Assert
		self.assertEqual(result, True)

	def test_is_url_an_html_page__cnn__returns_true(self):
		# Arrange
		url = "https://www.cnn.com"

		# Act
		result = is_url_an_html_page(url)

		# Assert
		self.assertEqual(result, True)

	def test_is_url_an_html_page__nerdthoughts__returns_true(self):
		# Arrange
		url = "http://www.nerdthoughts.com"

		# Act
		result = is_url_an_html_page(url)

		# Assert
		self.assertEqual(result, True)

	def test_is_url_an_html_page__ustif_otto_pdf__returns_falsee(self):
		# Arrange
		url = "https://ustifweb-stage.icfwebservices.com/documents/10184/10157/Otto's Service Station/2f432321-83eb-458f-abbb-0acb9e8dfe4b"

		# Act
		result = is_url_an_html_page(url)

		# Assert
		self.assertEqual(result, False)

	def test_is_url_an_html_page__dog_image__returns_falsee(self):
		# Arrange
		url = "https://farm2.static.flickr.com/1193/5133054365_0170d20672.jpg"

		# Act
		result = is_url_an_html_page(url)

		# Assert
		self.assertEqual(result, False)


	def test_need_to_short_circuit_url__no_env_variable__process(self):
		# Arrange

		# Act
		result = need_to_short_circuit_url("", "http://example.com/page1.html")

		# Assert
		self.assertEqual(result, False)

	def test_need_to_short_circuit_url__matching_env_variable__dont_process(self):
		# Arrange

		# Act
		result = need_to_short_circuit_url(".*example.com.*", "http://example.com/page1.html")

		# Assert
		self.assertEqual(result, True)	

	def test_need_to_short_circuit_url__matching_env_variable_pattern__dont_process(self):
		# Arrange

		# Act
		result = need_to_short_circuit_url(".*example.com.*|.*hiv.gov.*", "http://example.com/page1.html")
		result_2 = need_to_short_circuit_url(".*example.com.*|.*hiv.gov.*", "http://hiv.gov/page1.html")

		# Assert
		self.assertEqual(result, True)				
		self.assertEqual(result_2, True)


	def test_need_to_short_circuit_url__not_matching_env_variable__process(self):
		# Arrange

		# Act
		result = need_to_short_circuit_url(".*example.com.*|.*hiv.gov.*", "http://process.com/page1.html")

		# Assert
		self.assertEqual(result, False)				

	def test_need_to_short_circuit_url__icf_blog__process(self):
		# Arrange

		# Act
		result = need_to_short_circuit_url(".*hiv.gov.*", "https://www.icf.com/blog")

		# Assert
		self.assertEqual(result, False)	


	def test_continue_to_process_link__icf_blog__process(self):
		# Arrange

		# Act
		result = continue_to_process_link("", "https://www.icf.com/blog")

		# Assert
		self.assertEqual(result, True)	

	def test_continue_to_process_link__icf_blog_short_circuit__process(self):
		# Arrange

		# Act
		result = continue_to_process_link(".*icf.com.*", "https://www.icf.com/blog")

		# Assert
		self.assertEqual(result, False)	

if __name__ == '__main__':
	unittest.main()		


