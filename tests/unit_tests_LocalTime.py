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
		assert " UTC)" in results, "Expected string to have UTC)"

	def test_now__NY__format_has_both(self):
		# Arrange
		subject = LocalTime()		
		
		# Act
		results = subject.now()
		assert " (" in results, "Expected string to have ("
		assert ")" in results, "Expected string to have )"
		assert "America/New_York" in results, "Expected string to have America/New_York"	

	def test_get_utc_epoch__no_args__returns_epoch_number(self):
		# Arrange
		subject = LocalTime()

		# Act
		utc_epoch = subject.get_utc_epoch()

		# Assert
		self.assertGreater(utc_epoch, 1530932748)


	def test_get_ttl_epoch__no_args__more_than_current_epoch(self):
		# Arrange
		local_time = LocalTime()
		current_utc_epoch = local_time.get_utc_epoch()

		# Act
		expiration_epoch = local_time.get_epoch_plus_seconds(5)

		# Assert
		self.assertTrue(expiration_epoch > current_utc_epoch, "Want " + str(expiration_epoch) + " > " + str(current_utc_epoch))		

if __name__ == '__main__':
	unittest.main()		


