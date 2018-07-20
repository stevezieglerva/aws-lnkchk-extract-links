import requests

class Page():
	def __init__(self, url):
		self.url = url
		self.response_code = 0
		self.html = ""
		self.extract_links = {}
		self.html_page = False

		self.download()


	def download(self):
		response = requests.get(self.url, timeout=30)
		self.html = response.text
		self.response_code = response.status_code

		if "Content-Type" in response.headers:
			if "text/html" in response.headers["Content-Type"]:
				self.html_page = True
			else:
				self.html_page = False


	



