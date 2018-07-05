import datetime
import pytz


class LocalTime:
	def __init__(self, local_timezone = "America/New_York"):
		self.local_timezone = local_timezone
		self.utc = pytz.utc.localize(datetime.datetime.utcnow())
		self.local = self.utc.astimezone(pytz.timezone(self.local_timezone))

	def __str__(self):
		formatted = str(self.local) + " " + self.local_timezone + " (" + str(self.utc) + " UTC)"
		return formatted
		

	def now(self):
		self.utc = pytz.utc.localize(datetime.datetime.utcnow())
		self.local = self.utc.astimezone(pytz.timezone(self.local_timezone))
		return str(self)