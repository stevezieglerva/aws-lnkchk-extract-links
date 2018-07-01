import unittest
import boto3
from ESLambdaLog import *


class TestMethods(unittest.TestCase):
	def test_constructor__index_exists__object_created(self):
		# Arrange
		
		# Act
		subject = ESLambdaLog()
		results = subject.list_indices()

		# Assert
		assert len(results) > 0

	def test_log_event__simple_event__event_added_to_es(self):
		## Arrange
		subject = ESLambdaLog()	

		## Act
		event = { "Record" : {"name" : "test event a"}}
		subject.log_event(event)

		## Assert

	def test_log_event__different_index_name__event_added_to_es(self):
		## Arrange
		subject = ESLambdaLog("aws_test_index")	

		## Act
		event = { "Record" : {"name" : "test event b into aws_test_index"}}
		subject.log_event(event)

		## Assert

	def test_log_event__event_with_array__event_added_to_es(self):
		## Arrange
		subject = ESLambdaLog()	

		## Act
		event = { "Record" : {"name" : "test event a", "values" : [1, 2, 3]}}
		subject.log_event(event)

		## Assert


	def test_list_indices__valid_request__at_least_one_index_returned(self):
		## Arrange
		subject = ESLambdaLog()	

		# Act
		results = subject.list_indices()
		print(json.dumps(results, indent=True))

		# Assert
		assert len(results) > 0

if __name__ == '__main__':
	unittest.main()		


