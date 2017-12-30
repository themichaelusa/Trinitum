import rethinkdb as r

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
		
		#self.strat = strat
		#self.connObj = conn
		#self.dbReference = dbReference
		self.rwQueue = AsyncReadWriteQueue(self.classDict)

	def setTradingParameters(self, symbol, quantity, strategy, profile):
		self.classDict['strategy'].strategy = strategy
		self.classDict['pipeline'].symbol = symbol
		tradingClass = self.classDict['trading']
		tradingClass.symbol = symbol
		tradingClass.quantity = quantity
		tradingClass.profile = profile
		#tradingClass.tolerance = tolerance
		#tradingClass.poslimit = poslimit

	"""
	def setRiskProfile(self, profile):
		if profile is not None:
			self.classDict['trading'].riskProfile = profile
	"""

	def read(self, tableName, operation, *opargs): 
		self.rwQueue.cdRead(tableName, operation, *opargs)

	def write(self, tableName, operation, *opargs): 
		self.rwQueue.cdWrite(tableName, operation, *opargs)

	def processTasks(self):
		return self.rwQueue.processTasks() 

	def collectInstData(self):	
		statistics, books = "statistics", "books"
		self.read(statistics, "pullRiskStatistics")
		self.read(statistics, "pullCapitalStatistics")
		self.read(books, "getOrderBook")
		self.read(books, "getPositionBook")
		return self.processTasks()
