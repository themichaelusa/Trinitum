import time
#import rethinkdb as r

""" 
The TradingInstance class is the operational hub of Trinitum.
It's purpose is to take the information provided by the Gem object
and perform trading activities with it.
"""

class TradingInstance(object):
	
	def __init__(self, name, strategy, profile=None):

		self.name, self.NONE = name, "None"
		self.strategy, self.profile = strategy, profile
		self.auth, self.exchange, self.symbol, self.quantity = (None,)*4
				
		from .Constants import DEFAULT_IND_LAG, DEFAULT_SYS_LAG 
		self.indicatorLag, self.systemLag = DEFAULT_IND_LAG, DEFAULT_SYS_LAG

		self.conn = None
		self.dbRef = None
		self.databaseManager = None
		self.logger = None
	
	"""
	The initDatabase function has one purpose; create a local RethinkDB
	instance using the name provided by the Gem class.
	"""
	def initDatabase(self, hostname="localhost", port=28015): 

		#from Utilities import createRDB_Instance
		#createRDB_Instance()
		#print("CREATING RETHINK_DB INSTANCE")
		#time.sleep(5)
		
		import rethinkdb as r
		r.db_create(self.name).run(r.connect(hostname, port))
		self.conn = r.connect(hostname, port)
		self.dbRef = r.db(self.name)

	"""
	The initPipelineTables function has one purpose; create 2 tables inside
	our RethinkDB instance: SpotData, TechIndicators. Our 2 new tables then
	get dictionaries to base their structure off, as it is static; which means
	our tables will only be updated, ergo, their schemas never change. 
	"""
	"""
	def initPipelineTables(self): 

		spotData = {
		"trade_id": self.NONE,
		"price": self.NONE,
		"size": self.NONE,
		"bid": self.NONE,
		"ask": self.NONE,
		"volume": self.NONE,
		"time": self.NONE
		}

		techIndicators = dict.fromkeys(self.techInds)
		spotDataStr, techIndsStr = 'SpotData', 'TechIndicators'
		self.dbRef.table_create(spotDataStr).run(self.conn)
		self.logger.addEvent('database', 'CREATED: ' + spotDataStr)
		self.dbRef.table(spotDataStr).insert(spotData).run(self.conn)
		self.dbRef.table_create(techIndsStr).run(self.conn)
		self.logger.addEvent('database', 'CREATED: ' + techIndsStr)
		self.dbRef.table(techIndsStr).insert(techIndicators).run(self.conn)

	"""
	"""
	The initStatisticsTables function has one purpose; create 2 tables inside
	our RethinkDB instance: RiskData, CaptialData. Our 2 new tables then
	get dictionaries to base their structure off, as it is static; which means
	our tables will only be updated, ergo, their schemas never change. 
	"""
	"""
	def initStatisticsTables(self): 

		capitalData = {
		'capital' : self.NONE, 
		"commission" : self.NONE, 
		"return" : self.NONE
		}

		riskData = {}

		riskDataStr, CapitalDataStr = 'RiskData', 'CapitalData'
		self.dbRef.table_create(riskDataStr).run(self.conn)
		self.logger.addEvent('database', 'CREATED: ' + riskDataStr)
		self.dbRef.table(riskDataStr).insert(riskData).run(self.conn)
		self.dbRef.table_create(CapitalDataStr).run(self.conn)
		self.logger.addEvent('database', 'CREATED: ' + CapitalDataStr)
		self.dbRef.table(CapitalDataStr).insert(capitalData).run(self.conn)

	"""

	"""
	The initTradingTable function has one purpose; create a PositionCache table
	to store our ongoing postions. This table is dynamic, so we can add additional 
	Positions and then remove them as we please.
	"""
	def initTradingTable(self): 
		pCacheStr = 'PositionCache'
		self.dbRef.table_create(pCacheStr).run(self.conn)
		self.logger.addEvent('database', 'CREATED: ' + pCacheStr)

	"""
	The initStatisticsTables function has one purpose; create 2 tables inside
	our RethinkDB instance: OrderBook, PositionBook.This table is dynamic, 
	so we can add additional Orders and Positions as the Gem keeps trading.
	"""
	def initBookTables(self):
		#orderBookStr, PositionBookStr = 'OrderBook', 'PositionBook'
		#self.dbRef.table_create(orderBookStr).run(self.conn)
		#self.logger.addEvent('database', 'CREATED: ' + orderBookStr)
		positionBook = 'PositionBook'
		self.dbRef.table_create(positionBook).run(self.conn)
		self.logger.addEvent('database', 'CREATED: ' + positionBook)

	def setSymbol(self, exchange, symbol, quantity):
		self.exchange, self.symbol, self.quantity = exchange, symbol, quantity

	def setExchangeAuthCredentials(self, key, secret, passphrase):
		self.auth = (key, secret, passphrase)

	def setLagParams(self, indicatorLag, systemLag):
		self.indicatorLag, self.systemLag = indicatorLag, systemLag

	"""
	The generateTechIndObjects function creates realtime_talib Indicator objects 
	for every indicator adds with the Gem object method addIndicator. They are used 
	for calculating the specified TA-Lib indicators in real time, and sending them out
	to the TechIndicators table in the RethinkDB instance.
	"""
	def generateTechIndObjects(self, histDF):
		from realtime_talib import Indicator
		return [Indicator(histDF,k,*v) for k,v in self.strategy.indicators.items()]

	"""
	The createLoggerInstance function imports and creates a Logger object, which is responsible 
	for writing to the syslog everytime it's addEvent method is called. The object is passed 
	into the individual classes that make up AsyncManager.py through the instantiation of the 
	DatabaseManager object in the start function.
	"""
	def createLoggerInstance(self, logName):
		from .Diagnostics import Logger
		self.logger = Logger(logName)

	"""
	The start function creates the RethinkDB instance 
	"""
	def start(self):
	
		self.initDatabase()
		#self.initPipelineTables()
		#self.initStatisticsTables()
		self.initTradingTable()
		self.initBookTables()

		from .DatabaseManager import DatabaseManager
		self.databaseManager = DatabaseManager(self.dbRef, self.conn, self.auth, self.logger)
		self.databaseManager.setTradingParameters(self.symbol, self.quantity, self.strategy, self.profile)

	def run(self, endTime, histInterval, histPeriod, endCode): 

		from .Pipeline import Pipeline
		plInstance = Pipeline(histInterval)
		histData = plInstance.getCryptoHistoricalData(self.symbol, endTime, histPeriod)
		rttInds = self.generateTechIndObjects(histData)
		self.DatabaseManager.setPipelineParameters(self.symbol, rttInds)

		sysStart = 'TRADING_INSTANCE ' + self.name + ' INIT'
		self.logger.addEvent('system', sysStart)

		while (endTimeUNIX > getCurrentTimeUNIX()):
			self.runSystemLogic()
		self.end(endCode)

	def runSystemLogic(self):

		try:
			self.databaseManager.write("pipeline", "updateSpotData")
			self.databaseManager.write("statistics", "updateCapitalStatistics")
			self.databaseManager.read("statistics", "pullCapitalStatistics")
			capitalStats = self.databaseManager.processTasks()

			self.databaseManager.write("pipeline", "updateTechIndicators", self.techInds, self.indicatorLag)
			self.databaseManager.read("pipeline", "pullPipelineData")
			stratData = self.databaseManager.processTasks()
			spotPrice = stratData['price']

			self.databaseManager.execute("strategy", "tryStrategy", stratData)
			stratVerdict = self.databaseManager.processTasks()

			self.databaseManager.execute('trading', 'createOrders', stratVerdict)
			entryOrder = self.databaseManager.processTasks()
			potentialEntryOrder = bool(entryOrder != None)

			self.databaseManager.write("statistics", "updateCapitalStatistics", potentialEntryOrder)
			self.databaseManager.execute('trading', 'verifyAndEnterPosition', entryOrder, capitalStats, spotPrice)
			filledOrder, entryPos = self.databaseManager.processTasks()
			potentialPositionEntry = bool(filledOrder != [None])
			
			self.databaseManager.write('trading', 'addToPositionCache', entryPos)
			self.databaseManager.write('books', 'addToOrderBook', filledOrder)
			self.databaseManager.write("statistics", "updateCapitalStatistics", potentialPositionEntry)
			self.databaseManager.execute('trading', 'exitValidPositions', stratVerdict)
			filledExitOrders, completedPositions = self.databaseManager.processTasks()
			potentialExitMade = bool(potentialPositionEntry or filledExitOrders != [None])

			self.databaseManager.write("statistics", "updateCapitalStatistics", potentialExitMade)
			self.databaseManager.write('books', 'addToPositionBook', completedPositions)
			self.databaseManager.write('books', 'addToOrderBook', filledExitOrders)
			self.databaseManager.processTasks(), time.sleep(self.systemLag)
  			
		except BaseException as e:
			from .Utilities import getStackTrace
			stackTrace = getStackTrace(e)
			self.logger.addEvent('system', ('SYS_LOGIC_CRASH: ' + str(e)))
			self.logger.addEvent('system', ('SYS_LOGIC_CRASH_STACKTRACE: ' + str(stackTrace)))

	"""logic to close all remaining positions in cache, add to oBook, pBook.
	endCode decides a hard exit or soft exit, e.g wait for strategies
	or close out of all positions regardless of strats
	"""
	def end(self, endCode): 

		from .Constants import SOFT_EXIT, HARD_EXIT
		#TODO: Verify the safety and robustness of the SOFT_EXIT

		if (endCode == SOFT_EXIT): 
			try:
				self.logger.addEvent('system', "SOFT_EXIT INITIATED. ALL ONGOING TRADES BEING FINALIZED.")
				tradingRef = self.dbRef.table("PositionCache")
				while (int(tradingRef.count().run(self.conn)) > 0):
					self.runSystemLogic()
			except BaseException as e:
				from .Utilities import getStackTrace
				stackTrace = getStackTrace(e)
				self.logger.addEvent('system', ('SOFT_EXIT_FAILURE: ' + str(e)))
				self.logger.addEvent('system', ('SOFT_EXIT_FAILURE_STACKTRACE: ' + str(stackTrace)))

		if (endCode == HARD_EXIT):
			try:
				self.logger.addEvent('system', "HARD_EXIT INITIATED. ALL ONGOING TRADES TERMINATED.")
				self.databaseManager.read('trading', 'exitValidPositions', HARD_EXIT)
				filledExitOrders, completedPositions = self.databaseManager.processTasks()

				self.databaseManager.write("statistics", "updateCapitalStatistics")
				self.databaseManager.write('books', 'addToPositionBook', completedPositions)
				self.databaseManager.write('books', 'addToOrderBook', filledExitOrders)
				self.databaseManager.processTasks()
			except BaseException as e:
				from .Utilities import getStackTrace
				stackTrace = getStackTrace(e)
				self.logger.addEvent('system', ('HARD_EXIT_FAILURE: ' + str(e)))
				self.logger.addEvent('system', ('HARD_EXIT_FAILURE_STACKTRACE: ' + str(stackTrace)))

		rStats, cStats, oBook, pBook = self.databaseManager.collectInstData()
		sysEnd = 'TRADING_INSTANCE ' + self.name + ' END'
		self.logger.addEvent('system', sysEnd)
		from rethinkdb import db_drop
		db_drop(self.name).run(self.conn)

		# RDB directory removal too unintuitive for end user 
		#from .Utilities import removeRDB_Direc
		#removeRDB_Direc()

		from .Diagnostics import ResultFormatter
		results = ResultFormatter(self.name, self.logger.filename)
		results.getFormattedResults(rStats, cStats, oBook, pBook)
