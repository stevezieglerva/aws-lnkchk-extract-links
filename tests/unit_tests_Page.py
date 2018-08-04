import unittest
import json
from Page import *
import sys
import logging
import structlog



class PageTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

		structlog.configure(
			processors=[
				structlog.stdlib.filter_by_level,
				structlog.stdlib.add_logger_name,
				structlog.stdlib.add_log_level,
				structlog.stdlib.PositionalArgumentsFormatter(),
				structlog.processors.TimeStamper(fmt="iso"),
				structlog.processors.StackInfoRenderer(),
				structlog.processors.format_exc_info,
				structlog.processors.UnicodeDecoder(),
				structlog.processors.JSONRenderer()
			],
			context_class=dict,
			logger_factory=structlog.stdlib.LoggerFactory(),
			wrapper_class=structlog.stdlib.BoundLogger,
			cache_logger_on_first_use=True,
			)
		
		
		log = structlog.getLogger()
		log.critcal("starting testing")


	@classmethod
	def tearDownClass(cls):
		log = structlog.getLogger()
		log.critical("finished testing")


	def setUp(self):
		self.log = structlog.getLogger()

	def test_constructor__valid_url__html_download(self):
		# Arrange

		# Act
		subject = Page("https://www.cnn.com")

		# Assert
		self.assertIn("html", subject.html.lower(), "Expected page html to be returned")
		self.assertEqual(subject.response_code, 200, "Expected valid response code")		
		self.assertGreater(len(subject.extracted_links), 10, "Expected some extracted links")

	def test_constructor__redirect_url__html_download(self):
		# Arrange

		# Act
		subject = Page("http://cnn.com")

		# Assert
		self.assertIn("html", subject.html.lower(), "Expected page html to be returned")
		self.assertEqual(subject.response_code, 200, "Expected valid response code")		
		self.assertEqual(subject.html_page, True, "Expected HTML content type")		

	def test_constructor__image__not_html_page(self):
		# Arrange

		# Act
		subject = Page("https://farm2.static.flickr.com/1193/5133054365_0170d20672.jpg")

		# Assert
		self.assertNotIn("html", subject.html.lower(), "Did not expect HTML")
		self.assertEqual(subject.response_code, 0, "Expected valid response code")
		self.assertEqual(subject.html_page, False, "Did not expected HTML content type")		

	def test_constructor__large_zip__skipped_downloading(self):
		# Arrange

		# Act
		subject = Page("http://ipv4.download.thinkbroadband.com/100MB.zip")

		# Assert
		self.assertNotIn("html", subject.html.lower(), "Did not expect HTML")
		self.assertEqual(subject.response_code, 0, "Expected valid response code")



	def test_is_url_an_html_page__html__html_page(self):
		# Arrange

		# Act
		subject = Page("http://cnn.com")
		result = subject.is_url_an_html_page()

		# Assert
		self.assertEqual(result, True, "Expected HTML file")

	def test_is_url_an_html_page__image__not_html_page(self):
		# Arrange

		# Act
		subject = Page("https://farm2.static.flickr.com/1193/5133054365_0170d20672.jpg")
		result = subject.is_url_an_html_page()

		# Assert
		self.assertEqual(result, False, "Expected image file")

	def test_constructor__string_version_of_object__contains_correct_text(self):
		# Arrange
		subject = Page("https://www.cnn.com")

		# Act
		result = str(subject)

		# Assert
		self.assertIn("html_length", result, "Expected some JSON text")

	def test_constructor__hardcoded_html_with_absolute_links__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'>Click here for CNN</a><a href='http://www.google.com'>Click here for Google</a></html>"

		# Act
		subject = Page("http://www.absolute_example.com", html)
		subject_str = str(subject)
		subject_json_obj = json.loads(subject_str)
		self.log.info(json.dumps(subject_json_obj, indent=3))
		result = subject.extracted_links

		# Assert
		self.assertEqual(len(result), 2)
		found = False
		for link in result:
			if link.url_qualified == "http://www.cnn.com" and link.link_text == "Click here for CNN":
				found = True
		self.assertTrue(found, "Expected to find the extracted link")
		found = False
		for link in result:
			if link.url_qualified == "http://www.google.com" and link.link_text == "Click here for Google":
				found = True
		self.assertTrue(found, "Expected to find the extracted link")		

	def test_constructor__hardcoded_html_with_relative_links__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'>Click here for CNN</a><a href='/sports'>Click here for Sports</a></html>"

		# Act
		subject = Page("http://www.relative_example.com", html)
		subject_str = str(subject)
		subject_json_obj = json.loads(subject_str)
		self.log.info(json.dumps(subject_json_obj, indent=3))
		result = subject.extracted_links

		# Assert
		self.assertEqual(len(result), 2)
		found = False
		for link in result:
			if link.url_qualified == "http://www.cnn.com" and link.link_text == "Click here for CNN":
				found = True
		self.assertTrue(found, "Expected to find the extracted link")
		found = False
		for link in result:
			if link.url_qualified == "http://www.relative_example.com/sports" and link.link_text == "Click here for Sports":
				found = True
		self.assertTrue(found, "Expected to find the extracted link")


	def test_constructor__hardcoded_html_with_relative_no_slash_links__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'>Click here for CNN</a><a href='sports'>Click here for Sports</a></html>"

		# Act
		subject = Page("http://www.relative_example.com", html)
		result = subject.extracted_links

		# Assert
		self.assertEqual(len(result), 2)
		found = False
		for link in result:
			if link.url_qualified == "http://www.relative_example.com/sports" and link.link_text == "Click here for Sports":
				found = True
		self.assertTrue(found, "Expected to find the extracted link")

	def test_constructor__hardcoded_html_with_relative_and_query_strings__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'>Click here for CNN</a><a href='sports?id=33232&source=abc'>Click here for Sports</a></html>"

		# Act
		subject = Page("http://www.query_strings_example.com", html)
		result = subject.extracted_links

		# Assert
		self.assertEqual(len(result), 2)
		found = False
		for link in result:
			if link.url_qualified == "http://www.query_strings_example.com/sports?id=33232&source=abc" and link.link_text == "Click here for Sports":
				found = True
		self.assertTrue(found, "Expected to find the extracted link")		

	def test_constructor__hardcoded_html_with_pure_anchor_link__returns_links(self):
		# Arrange
		html = "<html><a href='http://www.cnn.com'>Click here for CNN</a><a href='#top'>Click here for Top</a></html>"

		# Act
		subject = Page("http://www.anchor_example.com", html)
		result = subject.extracted_links

		# Assert
		self.assertEqual(len(result), 1)


	def test_constructor__no_link_text__returns_links(self):
		# Arrange
		html = "<html><a href='https://www.cnn.com'/></html>"

		# Act
		subject = Page("http://www.no_link_text_example.com", html)
		result = subject.extracted_links


		# Assert
		self.assertEqual(len(result), 1)
		found = False
		for link in result:
			if link.url_qualified == "https://www.cnn.com" and link.link_text == "":
				found = True
		self.assertTrue(found, "Expected to find the extracted link")

	def test_constructor__https_link__returns_links(self):
		# Arrange
		html = "<html><a href='https://www.cnn.com'>Click here</a></html>"

		# Act
		subject = Page("http://www.https_example.com", html)
		result = subject.extracted_links

		# Assert
		self.assertEqual(len(result), 1)
		found = False
		for link in result:
			if link.url_qualified == "https://www.cnn.com" and link.link_text == "Click here":
				found = True
		self.assertTrue(found, "Expected to find the extracted link")

if __name__ == '__main__':
	unittest.main()		
