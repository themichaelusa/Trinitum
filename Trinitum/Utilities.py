
#--------- USEFUL LIST OPERATION METHODS------------

def filterListByType(data, dataType):
	return list(filter(lambda x: isinstance(x, dataType), data))

def flattenList(listToFlatten):
	nestedList = any(isinstance(sl, list) for sl in listToFlatten) 
	if(nestedList == False): return listToFlatten
	return [item for sublist in list(listToFlatten) for item in sublist]

def extendList(listToExtend, extenMultiplier): 
	import itertools as itert
	extendedListTuple = tuple(itert.repeat(listToExtend, extenMultiplier))
	return list(itert.chain.from_iterable(zip(*extendedListTuple)))

#--------- USEFUL DATETIME/TIME OPERATIONS METHODS-------------

def getCurrentTime():
	from datetime import datetime
	return str(datetime.now())

def getCurrentDateStr():
	import time
	return time.strftime("%Y%m%d")

def getCurrentTimeUNIX():
	import time
	return time.time()

def getCurrentTimeString():
	import time
	import datetime as dt
	return str(dt.datetime.fromtimestamp(time.time()))

def dateToUNIX(date): #format: "YYYYMMDD hhmmss"
	import time
	import ciso8601
	ts = ciso8601.parse_datetime(date)
	return time.mktime(ts.timetuple())

def UNIXtoDate(timestamp): 
	import datetime as dt
	return dt.datetime.fromtimestamp(int(timestamp))

def stringToDatetime(string): #format: "YYYYMMDD", ex: "20170519"
	return UNIXtoDate((dateToUNIX(string)))

def datetimeDiff(datetime1, daysNum, order = "%Y%m%d"):
	from datetime import datetime, timedelta
	formattedDT = datetime1[:10].replace("-", "")
	now = datetime.strptime(formattedDT, order).date()
	return str(now - timedelta(days=daysNum)).replace("-", "")

#--------- DICT OPERATION METHODS---------------------

def getObjectDict(obj):
	return dict((key, getattr(obj, key)) for key in dir(obj) if key not in dir(obj.__class__))

#--------- ERROR HANDLING METHODS---------------------

def getStackTrace(ex):
	import traceback
	return str("".join(traceback.format_exception(etype=type(ex),value=ex,tb=ex.__traceback__)))

#--------- RETHINKDB METHODS---------------------

def createRDB_Instance():
	
	from sys import executable
	from subprocess import Popen
	Popen([executable, 'rethinkdb'], shell=True)

	#from subprocess import call
	#call(['rethinkdb'], shell=True)

def removeRDB_Direc():
	from subprocess import call
	call(['rm', '-rf', 'rethinkdb_data'])
	