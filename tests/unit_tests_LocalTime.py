import unittest
from LocalTime import *


class TestMethods(unittest.TestCase):
	def test_constructor__NY__local_time_is_less(self):
		# Arrange
		
		# Act
		subject = LocalTime()
		print(str(subject))
		assert subject.local == subject.utc, "Expected NY time to equal UTC given the library"

	def test_str__NY__format_has_both(self):
		# Arrange
		subject = LocalTime()		
		
		# Act
		results = str(subject)
		assert " (" in results, "Expected string to have ("
		assert ")" in results, "Expected string to have )"
		assert "America/New_York" in results, "Expected string to have America/New_York"

	def test_now__NY__format_has_both(self):
		# Arrange
		subject = LocalTime()		
		
		# Act
		results = subject.now()
		assert " (" in results, "Expected string to have ("
		assert ")" in results, "Expected string to have )"
		assert "America/New_York" in results, "Expected string to have America/New_York"		

if __name__ == '__main__':
	unittest.main()		


