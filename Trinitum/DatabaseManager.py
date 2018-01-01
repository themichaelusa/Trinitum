
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

	def setTradingParameters(self, symbol, quantity, strategy, profile):
		self.classDict['strategy'].strategy = strategy
		tradingClass = self.classDict['trading']
		tradingClass.symbol = symbol
		tradingClass.quantity = quantity
		tradingClass.profile = profile

	def setPipelineParameters(self, symbol, inds):
		plRef = self.classDict['pipeline']
		plRef.symbol = symbol
		plRef.techInds = inds
		plRef.spotInds = {ind.tbWrapper.indicator: None for ind in inds}

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
		self.read(statistics, "pullRiskStatistics")
		self.read(statistics, "pullCapitalStatistics")
		self.read(books, "getOrderBook")
		self.read(books, "getPositionBook")
		return self.processTasks()
