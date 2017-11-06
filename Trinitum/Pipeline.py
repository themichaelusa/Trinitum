import time
import json
from .Utilities import dateToUNIX, flattenList
import pandas as pd
import numpy as np

class Pipeline(object):

	def __init__(self, interval): 

		self.interval = interval
		self.POLO_URL = 'https://poloniex.com/public'
		self.POLO_HIST_DATA = self.POLO_URL + '?command=returnChartData&currencyPair={}&start={}&end={}&period={}'

	def getCryptoHistoricalData(self, currencyPair, startDate, endDate, vwap = False):

		stDateUNIX = dateToUNIX(startDate)
		eDateUNIX = dateToUNIX(endDate)
		poloniexJsonURL = self.POLO_HIST_DATA.format(currencyPair, stDateUNIX, eDateUNIX, self.interval)

		import requests
		poloniexJson = requests.get(poloniexJsonURL).json()

		histDataframe = pd.DataFrame.from_records(poloniexJson)
		histDataframe.drop('quoteVolume', axis=1, inplace=True)
		histDataframe.drop('weightedAverage', axis=1, inplace=True)
		histDataframe['date'] = histDataframe['date'].astype(float)

		return histDataframe[["date", "open", "high", "low", "close", "volume"]]

	def getRiskFreeRate(self):
		from bs4 import BeautifulSoup
		import requests
		treasuryURL = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield'
		data = requests.get(treasuryURL).text
		html = BeautifulSoup(data, 'lxml')

		targetYieldRow = html.find_all('tr', class_='evenrow')
		floatYield = targetYieldRow[len(targetYieldRow)-1]
		allYields = floatYield.find_all('td', class_='text_view_data')
		return float(allYields[2].text)

class Formatter(object):

	def __init__(self): pass

	def formatStratData(self, sdDict, tiDict, vwap=False):

		stratData = {
		'price': float(sdDict['price']),
		'volume': float(sdDict['volume'])
		}

		tiDict.pop('id')
		formattedTiDict = {}
		for k,v in tiDict.items():
			unnecessaryTuple = type(v) == list and len(v) == 1  
			if (unnecessaryTuple): formattedTiDict.update({k:v[0]})
			else: formattedTiDict.update({k:v})

		stratData.update(formattedTiDict)
		return stratData

	def generateVWAP(self, histDF): 
		v, h, l = histDF.v.values, histDF.h.values, histDF.l.values
		return np.cumsum(v*(h+l)/2)/np.cumsum(v)

	def dfToHeikenAshi(self, dataframe): pass
