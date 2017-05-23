import Constants as cst
import poloWrapper as pw
import googFinanceWrapper as gf
import talibWrapper as tbw
import Universe as uni
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

		self.unitsHistDataObjects = []
		self.unitsTalibDicts = []

	def pullSpotPrice(self, tickers, index):

		if (self.tradingType == "BT"):
			return # temp, will return 		

	def unpackWrappers(self, universe): 

		dateParams = (self.startDate, self.endDate)
		histWrappers = list(filter(lambda x: isinstance(x, uni.HistoricalDataWrapper), self.data))
		histDataObjects = [plu.HistoricalData(unit.ticker, unit.frequency, *dateParams) for unit in universe.units]
		
		self.unitsHistDataObjects.extend(histDataObjects)
		# self.unitsHistData.extend([unit.histData for unit in self.unitsHistDataObjects])

		techIndWrappers = list(set(self.data) - set(histWrappers))
		"""
		if (techIndWrappers == [] or techIndWrappers == None): return

		for wrapper in techIndWrappers:
			if (wrapper.frequency != self.tradingFreq):
			
		self.unitsTalibDicts.extend([tbw.generateInputDict(unit) for unit in self.unitsHistData])
		"""

	def generateDatasets(self): 

		histData = [unit.histData for unit in self.unitsHistDataObjects]
		laggedHistData = []
		technicalIndicators = [] 

		return tuple(reduce(lambda t1, t2: t1 + t2, (histData, technicalIndicators)))

class HistoricalData(object):

	def __init__(self, ticker, frequency, startDate, endDate):

		self.ticker = ticker
		self.poloniex = cst.NOT_SET
		self.histData = self.pullHistoricalData(frequency, startDate, endDate)
		
	def pullHistoricalData(self, startDate, endDate): 

		if (self.ticker in cst.CRYPTO_TICKERS):
			
			self.poloniex = pw.poloniex(*cst.POLO_PUBLIC_API)
			crypTicker = cst.CRYPTO_TICKERS[self.ticker]
			queryFields = {crypTicker, self.startDate, self.endDate, frequency}
			poloniexJson = self.poloniex.api_query("returnChartData", queryFields)

			return pd.DataFrame.from_records(poloniexJson)

		else:

			dataframe, datesToReturn = gf.getGoogleIntradayData(ticker, 60, 15) #temp
			self.talibInputDicts.append((ticker, talibDicts))

	def pullTechnicalIndicator(self, indicator, frequency): 

		tickerIndex = [i for i, v in enumerate(self.talibInputDicts) if v[0] == ticker]
		talibDict = self.talibInputDicts[tickerIndex][1]

