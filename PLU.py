import CONST as cst
import poloWrapper as pw
import googFinanceWrapper as gf
import talibWrapper as tbw
import Universe as uni
import Utilities as utl
import itertools

def pullSpotPrice(ticker): # temporary
	return 5 		

class PLU(object):
	
	def __init__(self, data, universe, startDate, endDate, tradingType):
		
		self.data = utl.flattenList(data) 
		self.startDate = startDate
		self.endDate = endDate

		self.tradingType = tradingType
		self.tradingFreq = universe.frequency
		self.techIndicatorWrapData = []
		self.unitsHistDataObjects = []

	"""def pullSpotPrice(self, tickers, index):
					
		if (self.tradingType == "BT"):
			return # temp, will return """		

	def unpackWrappers(self, universe): 

		if (self.tradingType == "BT"):

			dateParams = (self.startDate, self.endDate)
			histWrappers = utl.filterListByType(self.data, uni.HistoricalDataWrapper)
			histDataObjects = [HistoricalData(unit.ticker, unit.frequency, *dateParams) for unit in histWrappers]
			self.unitsHistDataObjects.extend(histDataObjects)

			techIndWrappers = utl.filterListByType(self.data, uni.TechnicalIndicatorWrapper)
			if (techIndWrappers == [] or techIndWrappers == None): return
			self.techIndicatorWrapData.extend([(t.indicator, t.frequency, *t.indicatorArgs) for t in techIndWrappers])

	def generateDatasets(self): 

		histData = [unit.histData for unit in self.unitsHistDataObjects]
		if (self.techIndicatorWrapData == []): return histData
		technicalIndicatorsDicts = [tbw.generateInputDict(unit) for unit in histData]

		rawTechInd = []
		for unit in technicalIndicatorsDicts:
			for wrapData in self.techIndicatorWrapData:
				rawTechInd.append((unit, *wrapData, self.tradingFreq))

		technicalIndicators = [pullTechnicalIndicator(*raw) for raw in rawTechInd]
		flattenedIndicators = utl.flattenList(technicalIndicators)
		return utl.flattenList((histData, flattenedIndicators))

	def formatToTickDatasets(self, datasets):

		historicalData, technicalIndicators = datasets 
		historicalTicks, indicatorTicks = [], []
		
		for t in historicalData:
			historicalTicks.append((t['close'], t['volume']))

		# add iteration for tech indicators
		# join both lists via datatime into tick by tick dataframe
		# return formatted dataframe 

class HistoricalData(object):

	def __init__(self, ticker, frequency, startDate, endDate):

		self.ticker = ticker
		self.frequency = frequency
		self.histData = self.pullHistoricalData(startDate, endDate)

	def pullHistoricalData(self, startDate, endDate): 

		if (self.ticker in cst.CRYPTO_TICKERS):
			
			crypTicker = cst.CRYPTO_TICKERS[self.ticker]
			unixPeriod = (utl.dateToUNIX(startDate), utl.dateToUNIX(endDate))
			queryFields = (crypTicker, *unixPeriod, self.frequency)
			return pw.getCryptoHistoricalData(*queryFields)

		else:

			formattedStart, formattedEnd = utl.stringToDatetime(startDate), utl.stringToDatetime(endDate) 
			period = utl.datetimeDiff(formattedStart, formattedEnd)
			return gf.getGoogleIntradayData(self.ticker, self.frequency, period) 
			 
def pullTechnicalIndicator(init, indicator, lag, tbArgs, tradingFreq): 

	talibWrapper = tbw.TalibHistWrapper(init, tbArgs)
	technicalIndicator = talibWrapper.getIndicator(indicator)
	extensionMultiplier = lag//tradingFreq
	if (extensionMultiplier <= 1): return technicalIndicator
	return [utl.extendList(ind, extensionMultiplier) for ind in technicalIndicator]
