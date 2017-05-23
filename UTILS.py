from datetime import datetime
import itertools as itert

def getCurrentTime():
	return str(datetime.now())

def extendList(listToExtend, extenMultiplier): 

	extendedListTuple = tuple(itert.repeat(listToExtend, extenMultiplier))
	return list(itert.chain.from_iterable(zip(*extendedListTuple)))

