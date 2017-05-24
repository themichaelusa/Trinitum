import CONST as cst
import poloWrapper as pw
import googFinanceWrapper as gf
import talibWrapper as tbw
import Universe as uni
import Utilities as ult
import pandas as pd

def pullSpotPrice(ticker):
	return 5 # temp		

class PLU(object):
	
	def __init__(self, data, universe, startDate, endDate, tradingType):
		
		self.data = list(data)
		self.tradingType = tradingType
		self.tradingFreq = universe.frequency
		self.startDate = startDate
		self.endDate = endDate

		self.techIndicatorWrapData = []
		self.unitsHistDataObjects = []
		self.techIndHistDataObjects = []

	def pullSpotPrice(self, tickers, index):

		if (self.tradingType == "BT"):
			return # temp, will return 		

	def unpackWrappers(self, universe): 

		if (self.tradingType == "BT"):

			dateParams = (self.startDate, self.endDate)
			histWrappers = list(filter(lambda x: isinstance(x, uni.HistoricalDataWrapper), self.data))
			histDataObjects = [plu.HistoricalData(unit.ticker, unit.frequency, *dateParams) for unit in histWrappers]
			self.unitsHistDataObjects.extend(histDataObjects)

			techIndWrappers = list(set(self.data) - set(histWrappers))
			if (techIndWrappers == [] or techIndWrappers == None): return
			self.techIndicatorWrapData.extend([(t.indicator, t.indicatorArgs) for t in techIndWrappers])
			techIndHDObjects = [plu.HistoricalData(unit.ticker, unit.frequency, *dateParams) for unit in techIndWrappers]
			self.techIndHistDataObjects.extend(techIndHDObjects)

	def generateDatasets(self): 

		histData = [unit.histData for unit in self.unitsHistDataObjects]
		technicalIndHistData = [unit.histData for unit in self.techIndHistDataObjects]
		technicalIndicatorsDicts = [tbw.generateInputDict(unit) for unit in technicalIndHistData]

		techIndicatorParams = list(zip(technicalIndicatorsDicts, self.techIndicatorWrapData))
		technicalIndicators = [u.pullTechnicalIndicator(*unit) for unit in techIndicatorParams]

		return tuple(reduce(lambda t1, t2: t1 + t2, (histData, technicalIndicators)))

class HistoricalData(object):

	def __init__(self, ticker, frequency, startDate, endDate):

		self.ticker = ticker
		self.frequency = frequency
		self.poloniex = cst.NOT_SET
		self.histData = self.pullHistoricalData(startDate, endDate)
		
	def pullHistoricalData(self, startDate, endDate): 

		if (self.ticker in cst.CRYPTO_TICKERS):
			
			self.poloniex = pw.poloniex(*cst.POLO_PUBLIC_API)
			crypTicker = cst.CRYPTO_TICKERS[self.ticker]
			queryFields = {crypTicker, startDate, endDate, self.frequency}
			poloniexJson = self.poloniex.api_query("returnChartData", queryFields)

			return pd.DataFrame.from_records(poloniexJson)

		else:

			period = utl.datetimeDiff(endDate, startDate)
			return gf.getGoogleIntradayData(ticker, self.frequency, period) 
			 
	def pullTechnicalIndicator(self, init, indicator, tbArgs): 

		talibWrapper = tbw.TalibHistWrapper(init, *tbArgs)
		return talibWrapper.getIndicator(indicator)

