import unittest
from lambda_function import *
import boto3
from datetime import datetime


class TestMethods(unittest.TestCase):
	def test_aws_lnkchk_extract_links__valid_queue_message__lambda_called(self):
		# Arrange
		self.db = boto3.resource("dynamodb")
		queue = self.db.Table("lnkchk-queue")
		queue.put_item(Item = {"url": "http://nerdthoughts.net", "Timestamp" : str(datetime.now())})

		# Act
		print("Calling lambda_handler ...")
		lambda_handler({}, "")

		# Assert

##	def test_aws_lnkchk_extract_links__valid_queue_message_cnn__lambda_called(self):
##		# Arrange
##		sqs = boto3.client('sqs')
##		queue_url = 'https://queue.amazonaws.com/112280397275/lnkchk-pages'
##		#queue_url = sqs.get_queue_url(QueueName='lnkchk-pages') 
##		response = sqs.send_message(QueueUrl=queue_url, DelaySeconds=10, MessageBody='https://www.cnn.com',  MessageAttributes={
##			'file': {
##				'DataType': 'String',
##				'StringValue': 'integration_test.txt'
##			},
##			'line': {
##				'DataType': 'String',
##				'StringValue': '1'
##			},
##			'source': {
##				'DataType': 'String',
##				'StringValue': 'integration test'
##			}
##			})
##
##		# Act
##		print("Calling lambda_handler ...")
##		lambda_handler({}, "")
##
##		# Assert

if __name__ == '__main__':
	unittest.main()		


