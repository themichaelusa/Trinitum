from datetime import datetime
from dateutil import relativedelta
import itertools as itert
import matplotlib as mpl
import datetime as dt
import ciso8601
import time

#--------- USEFUL LIST OPERATION METHODS------------

def filterListByType(data, dataType):
	return list(filter(lambda x: isinstance(x, dataType), data))

def flattenList(objToFlatten):

	if (len(objToFlatten) == 0): return objToFlatten
	return [item for sublist in list(objToFlatten) for item in sublist]

def extendList(listToExtend, extenMultiplier): 

	extendedListTuple = tuple(itert.repeat(listToExtend, extenMultiplier))
	return list(itert.chain.from_iterable(zip(*extendedListTuple)))

#--------- USEFUL DATETIME/TIME OPERATIONS METHODS-------------

def getCurrentTime():
	return str(datetime.now())

def dateToUNIX(date):  #format: "YYYYMMDD hhmmss"
	ts = ciso8601.parse_datetime(date)
	return time.mktime(ts.timetuple())

def UNIXtoDate(timestamp): 
	return dt.datetime.fromtimestamp(int(timestamp))

def stringToDatetime(string): #format: "YYYYMMDD", ex: "20170519"
	return UNIXtoDate((dateToUNIX(string)))

def date2numWrapper(data): 
	return mpl.dates.date2num(data)

def num2dateWrapper(data): 
	return mpl.dates.num2date(data)

def datetimeDiff(datetime1, datetime2):
	return relativedelta.relativedelta(datetime2, datetime1).days
