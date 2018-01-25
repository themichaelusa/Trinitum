
class DatabaseManager(object):

	def __init__(self, dbReference, conn, auth, logger):
		from .AsyncManager import AsyncPipelineManager, AsyncStrategyManager
		from .AsyncManager import AsyncStatisticsManager, AsyncTradingManager
		from .AsyncManager import AsyncBookManager
		from AsyncPQ import AsyncReadWriteQueue

		self.classDict = {
		'pipeline': AsyncPipelineManager(dbReference, conn, logger),
		'strategy': AsyncStrategyManager(dbReference, conn, logger),
		'statistics': AsyncStatisticsManager(dbReference, conn, auth, logger),
		'trading': AsyncTradingManager(dbReference, conn, auth, logger),
		'books': AsyncBookManager(dbReference, conn, logger)
		}
	
		self.rwQueue = AsyncReadWriteQueue(self.classDict)

	def addCustomData(self, data):
		self.classDict['pipeline'].customData = data

	def setTradingParameters(self, symbol, quantity, strategy, profile, rParams):
		self.classDict['strategy'].strategy = strategy
		tradingClass = self.classDict['trading']
		tradingClass.symbol = symbol
		tradingClass.quantity = quantity
		tradingClass.params = rParams
		self.classDict['statistics'].riskProfile = profile

	def setPipelineParameters(self, symbol, inds, lag, customTables):
		plRef = self.classDict['pipeline']
		plRef.symbol = symbol
		plRef.techInds = inds
		plRef.indicatorLag = lag
		plRef.spotInds = {ind.tbWrapper.indicator: None for ind in inds}
		plRef.customTables = customTables

	def read(self, tableName, operation, *opargs): 
		self.rwQueue.cdRead(tableName, operation, *opargs)

	def write(self, tableName, operation, *opargs): 
		self.rwQueue.cdWrite(tableName, operation, *opargs)

	def execute(self, tableName, operation, *opargs): 
		self.read(tableName, operation, *opargs)

	def processTasks(self):
		return self.rwQueue.processTasks() 

	def collectInstData(self):	
		statistics, books = "statistics", "books"
		capStats = self.classDict['statistics'].getCapitalStats()
		riskStats = self.classDict['statistics'].getRiskStats(capStats['capital'])

		self.read(books, "getOrderBook")
		self.read(books, "getPositionBook")
		return (riskStats, capStats) + self.processTasks()
