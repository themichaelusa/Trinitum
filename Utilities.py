from datetime import datetime
from dateutil import relativedelta
import itertools as itert

def getCurrentTime():
	return str(datetime.now())

def extendList(listToExtend, extenMultiplier): 

	extendedListTuple = tuple(itert.repeat(listToExtend, extenMultiplier))
	return list(itert.chain.from_iterable(zip(*extendedListTuple)))

def dateToUNIX(date):  #format: "YYYYMMDD hhmmss"

	ts = ciso8601.parse_datetime(date)
	return time.mktime(ts.timetuple())

def UNIXtoDate(timestamp): 
	return dt.datetime.fromtimestamp(timestamp)

def date2numWrapper(data): 
	return mpl.dates.date2num(data)

def num2dateWrapper(data): 
	return mpl.dates.num2date(data)

def datetimeDiff(datetime1, datetime2):
	return relativedelta.relativedelta(datetime2, datetime1).days



