
class Pipeline(object):

	def __init__(self, interval): 
		self.interval = interval
		self.POLO_URL = 'https://poloniex.com/public'
		self.POLO_HIST_DATA = self.POLO_URL + '?command=returnChartData&currencyPair={}&start={}&end={}&period={}'

	def getCryptoHistoricalData(self, symbol, endTime, histPeriod, vwap=False):

		from .Constants import GDAX_TO_POLONIEX
		from .Utilities import dateToUNIX, getCurrentDateStr, datetimeDiff, getCurrentTimeUNIX

		endTimeUNIX = dateToUNIX(endTime)
		startDate = getCurrentDateStr()
		priorDate = datetimeDiff(startDate, histPeriod)
		gdaxTicker = GDAX_TO_POLONIEX[symbol]

		stDateUNIX = dateToUNIX(priorDate)
		eDateUNIX = dateToUNIX(startDate)
		poloniexJsonURL = self.POLO_HIST_DATA.format(gdaxTicker, stDateUNIX, eDateUNIX, self.interval)

		import json
		import requests
		poloniexJson = requests.get(poloniexJsonURL).json()

		from pandas import DataFrame
		histDataframe = DataFrame.from_records(poloniexJson)
		histDataframe.drop('quoteVolume', axis=1, inplace=True)
		histDataframe.drop('weightedAverage', axis=1, inplace=True)
		histDataframe['date'] = histDataframe['date'].astype(float)

		return histDataframe[["date", "open", "high", "low", "close", "volume"]]

class Formatter(object):

	def __init__(self): pass

	def formatStratData(self, sdDict, tiDict, vwap=False):
		stratData = {
		'price': float(sdDict['last']),
		'volume': float(sdDict['volume'])
		}

		formattedTiDict = {}
		for k,v in tiDict.items():
			unnecessaryTuple = type(v) == list and len(v) == 1  
			if (unnecessaryTuple): formattedTiDict.update({k:v[0]})
			else: formattedTiDict.update({k:v})

		return {**stratData, **formattedTiDict} # merged stratData & formattedTiDict

	def generateVWAP(self, histDF): 
		from numpy import cumsum
		v, h, l = histDF.v.values, histDF.h.values, histDF.l.values
		return cumsum(v*(h+l)/2)/cumsum(v)

	def dfToHeikenAshi(self, dataframe): pass

def getRiskFreeRate():
	from bs4 import BeautifulSoup
	import requests
	treasuryURL = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield'
	data = requests.get(treasuryURL).text
	html = BeautifulSoup(data, 'lxml')

	targetYieldRow = html.find_all('tr', class_='evenrow')
	floatYield = targetYieldRow[len(targetYieldRow)-1]
	allYields = floatYield.find_all('td', class_='text_view_data')
	return float(allYields[2].text)

"""
class DataBank:

	def __init__(self): 
		self.bank = {
			"BTC_BLOCKCHAIN_STATS": getBtcBlockchainStats,
		}

	def getBtcBlockchainStats(self):
		import requests
		return requests.get('https://api.blockchain.info/stats').json()

class DataStore:
	def __init__(self): 
		self.pool = {}
"""
		