import CONST as cst
import poloWrapper as pw
import googFinanceWrapper as gf

def pullSpotPrice(ticker):
	return 5 # temp		

"""class PLU(object):
	
	def __init__(self, arg):
		self.arg = arg"""

class Pipeline(object):

	def __init__(self, pipelineType, tradeFrequency):

		self.pipelineType = pipelineType
		self.tradeFrequency = tradeFrequency
		self.startDate = cst.NOT_SET
		self.endDate = cst.NOT_SET

		self.poloniex = pw.poloniex(*cst.POLO_PUBLIC_API)
		self.talibInputDicts = []

	def setPeriod(self, startDate, endDate):

		self.startDate = startDate
		self.endDate = endDate

	class HistoricalData(object):

		def __init__(self, ticker):
			super(HistData, self).__init__()
			self.arg = arg
			
	def pullHistoricalData(self, ticker): 

		if (ticker in cst.CRYPTO_TICKERS):
			
			crypTicker = cst.CRYPTO_TICKERS[ticker]
			queryFields = {crypTicker, self.startDate, self.endDate, self.tradeFrequency}
			self.poloniex.api_query("returnChartData", queryFields)

		else:

			dataframe, datesToReturn, talibDicts = gf.getGoogleIntradayData(ticker, 60, 15) #temp
			self.talibInputDicts.append((ticker, talibDicts))

		def generateTechIndicator(self, indicator, frequency): 

			tickerIndex = [i for i, v in enumerate(self.talibInputDicts) if v[0] == ticker]
			talibDict = self.talibInputDicts[tickerIndex][1]

pl = Pipeline("BT", 60)
amdHist = pl.pullHistoricalData("AMD")
amdHist.generateTechIndicator("RSI", 300)

