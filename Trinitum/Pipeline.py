import time
import json
import requests
import googFinanceWrapper as gf 
from Utilities import dateToUNIX, flattenList
import pandas as pd
import numpy as np

class Pipeline(object):

	def __init__(self, interval): 

		self.interval = interval
		self.POLO_URL = 'https://poloniex.com/public'
		self.POLO_HIST_DATA = self.POLO_URL + '?command=returnChartData&currencyPair={}&start={}&end={}&period={}'
		self.gfFinanceReference = gf.getGoogleIntradayData

	def getCryptoHistoricalData(self, currencyPair, startDate, endDate, vwap = False):

		stDateUNIX = dateToUNIX(startDate)
		eDateUNIX = dateToUNIX(endDate)
		poloniexJsonURL = self.POLO_HIST_DATA.format(currencyPair, stDateUNIX, eDateUNIX, self.interval)
		poloniexJson = requests.get(poloniexJsonURL).json()

		histDataframe = pd.DataFrame.from_records(poloniexJson)
		histDataframe.drop('quoteVolume', axis=1, inplace=True)
		histDataframe.drop('weightedAverage', axis=1, inplace=True)
		histDataframe['date'] = histDataframe['date'].astype(float)

		return histDataframe[["date", "open", "high", "low", "close", "volume"]]

	def getEquityHistoricalData(self, ticker, lookback):
		equityData = self.gfFinanceReference(ticker, self.interval, lookback)
		return equityData

class Formatter(object):

	def __init__(self): pass

	def formatSpotData(self, sdDict, vwap=False):
		
		spotData = [float(sdDict['price']), float(sdDict['volume'])]
		if (vwap == True): 
			spotData.append(float(sdDict['weightedAverage']))
			return spotData
		else: return spotData

	def formatTechIndicators(self, tiDict):
		
		dictVals = list(tiDict.values())
		dictVals = dictVals[:len(dictVals)-1] #removes rethinkDB ID
		return flattenList(dictVals)

	def dfToHeikenAshi(self, dataframe): pass
