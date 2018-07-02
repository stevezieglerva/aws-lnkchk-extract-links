import boto3
import re
import json
from datetime import datetime
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

class ESLambdaLog:
	def __init__(self, index_name = "aws_lambda_start"):
		self.index_name = index_name
		es_host = 'search-ziegler-es-bnlsbjliclp6ebc67fu3mfr74u.us-east-1.es.amazonaws.com'
		auth = BotoAWSRequestsAuth(aws_host=es_host,
											aws_region='us-east-1',
											aws_service='es')

		# use the requests connection_class and pass in our custom auth class
		self.es = Elasticsearch(host=es_host, use_ssl=True, port=443, connection_class=RequestsHttpConnection, http_auth=auth)	
		

		indices = self.list_indices()
		if self.index_name not in indices:
			log_info = { "event" : "Created " + self.index_name + " index", "@timestamp" : self.get_timestamp()}
			mappings = {
					"mappings": {
						"doc": {
							"properties": {
								"@timestamp": {
									"type": "date"
							}
						}
					}
				}
			}
			self.es.indices.create(self.index_name, body=mappings)
			self.es.index(index=self.index_name, doc_type = "doc", body = log_info)



	def get_timestamp(self):
		return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

	def log_event(self, event):
		event["@timestamp"] = self.get_timestamp()
		self.es.index(index=self.index_name, doc_type = "doc", body = event)

		#2018-02-01T00:00:00

	def list_indices(self):
		results = self.es.indices.get(index = "*")
		list = []
		for index_name in results.keys():
			list.append(index_name)
		return list