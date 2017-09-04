import rethinkdb as r
import AsyncManager as asm
from AsyncPQ import AsyncReadWriteQueue

class DatabaseManager(object):

	def __init__(self, dbReference, conn, strat, auth, logger):

		self.classDict = {
		'pipeline': asm.AsyncPipelineManager(dbReference, conn, logger),
		'strategy': asm.AsyncStrategyManager(dbReference, conn, strat, logger),
		'statistics': asm.AsyncStatisticsManager(dbReference, conn, auth, logger),
		'trading': asm.AsyncTradingManager(dbReference, conn, auth, logger),
		'books': asm.AsyncBookManager(dbReference, conn, logger)
		}
		
		self.strat = strat
		self.connObj = conn
		self.dbReference = dbReference
		self.rwQueue = AsyncReadWriteQueue(self.classDict)

	def setTradingParameters(self, symbol, quantity, tolerance, poslimit):

		tradingClass = self.classDict['trading']
		self.classDict['pipeline'].symbol = symbol
		tradingClass.symbol = symbol
		tradingClass.quantity = quantity
		tradingClass.tolerance = tolerance
		tradingClass.poslimit = poslimit

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
