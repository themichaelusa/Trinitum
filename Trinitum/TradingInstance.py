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
				
		from .Constants import (DEFAULT_IND_LAG, DEFAULT_SYS_LAG, 
			DEFAULT_CUSTOM_LOGIC, DEFAULT_CUSTOM_DATA)

		self.indicatorLag, self.systemLag = DEFAULT_IND_LAG, DEFAULT_SYS_LAG 
		self.customLogic, self.customData = DEFAULT_CUSTOM_LOGIC, DEFAULT_CUSTOM_DATA
		self.customTableRefs = {}

		self.conn = None
		self.dbRef = None
		self.databaseManager = None
		self.logger = None
	
	"""
	The initDatabase function has one purpose; create a local RethinkDB
	instance using the name provided by the Gem class.
	"""
	def initDatabase(self, hostname="localhost", port=28015, customTables=[]): 

		#from Utilities import createRDB_Instance
		#createRDB_Instance()
		#print("CREATING RETHINK_DB INSTANCE")
		#time.sleep(5)
		
		import rethinkdb as r
		r.db_create(self.name).run(r.connect(hostname, port))
		self.conn = r.connect(hostname, port)
		self.dbRef = r.db(self.name)

		for t in customTables:
			self.dbRef.table_create(t).run(self.conn)
			self.customTableRefs.update({t:self.dbRef.table(t)})
			self.logger.addEvent('database', 'CUSTOM TABLE CREATED: ' + t)

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
		orderBookStr, PositionBookStr = 'OrderBook', 'PositionBook'
		self.dbRef.table_create(orderBookStr).run(self.conn)
		self.logger.addEvent('database', 'CREATED: ' + orderBookStr)
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
	def generateTechIndObjects(self, histDF, indicators):
		from realtime_talib import Indicator
		return [Indicator(histDF,ind,*args) for ind,args in indicators]

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
	def start(self, endTime, histInterval, histPeriod, indicators, custTables):

		sysInit = 'TRADING_INSTANCE ' + self.name + ' SETUP INIT'
		self.logger.addEvent('system', sysInit)
		
		#### INIT RDB INSTANCE && CREATE TABLES ####
		self.initDatabase(customTables=custTables)
		self.initBookTables()

		#### DATABASE MANAGER INSTANTIATION && SETUP #####
		from .DatabaseManager import DatabaseManager
		self.databaseManager = DatabaseManager(self.dbRef, self.conn, self.auth, self.logger)
		self.databaseManager.setTradingParameters(self.symbol, self.quantity, self.strategy, self.profile, self.profile.parameters)

		#### PULL HISTORICAL DATA & GENERATE INDICATOR OBJECTS, PASS INTO DATABASE MANAGER
		from .Pipeline import Pipeline
		plInstance = Pipeline(histInterval)
		histData = plInstance.getCryptoHistoricalData(self.symbol, endTime, histPeriod)
		rttInds = self.generateTechIndObjects(histData, indicators)
		self.databaseManager.setPipelineParameters(self.symbol, rttInds, self.indicatorLag, self.customTableRefs)

		sysSetup = 'TRADING_INSTANCE ' + self.name + ' SETUP COMPLETE'
		self.logger.addEvent('system', sysSetup)

	def run(self, endTime, endCode, runTime): 
		from .Utilities import dateToUNIX
		endTimeUNIX = dateToUNIX(endTime)
		sysBegin = 'TRADING_INSTANCE ' + self.name + ' INIT'
		self.logger.addEvent('system', sysBegin)
		
		if runTime == None:
			while (endTimeUNIX > getCurrentTimeUNIX()):
				self.runSystemLogic()
		else:
			for t in range(runTime):
				self.runSystemLogic()
		self.end(endCode)

	def runSystemLogic(self):
		try:
			#### UPDATE STATISTICS AND UPDATE STRATEGY/RISK DATA ####
			self.databaseManager.execute("pipeline", "updateDefaultFeeds")
			self.databaseManager.execute("pipeline", "runCustomDataFeeds")
			self.databaseManager.write("statistics", "updateCapitalStatistics")
			self.databaseManager.execute('statistics', 'updateRiskStatistics')
			self.databaseManager.processTasks()

			self.databaseManager.read("pipeline", "getPipelineData")
			stratData = self.databaseManager.processTasks()

			spotPrice = stratData['price']
			availibleFunds = self.databaseManager.classDict['statistics'].getCapitalStats()['capital']
			riskData = self.databaseManager.classDict['statistics'].getRiskStats(availibleFunds)
			closedPositionCount = self.databaseManager.classDict['statistics'].getReturnsCount()

			#### TRY ENTRY STRATEGY, PLACE ORDERS, ENTER POSITIONS ####
			self.databaseManager.execute("strategy", "tryEntryStrategy", stratData, riskData, pCount=closedPositionCount)
			stratVerdict = self.databaseManager.processTasks()

			self.databaseManager.execute('trading', 'createOrders', stratVerdict)
			entryOrder = self.databaseManager.processTasks()
			potentialEntryOrder = bool(entryOrder != None)

			currentCapital = self.databaseManager.classDict['statistics'].getCapitalStats()['capital']
			self.databaseManager.write("statistics", "updateCapitalStatistics", potentialEntryOrder)
			self.databaseManager.execute('trading', 'verifyAndEnterPosition', entryOrder, currentCapital, spotPrice)
			filledEntryOrder, entryPos = self.databaseManager.processTasks()
			potentialPositionEntry = bool(filledEntryOrder != [None])
			
			#### TRY EXIT STRATEGY AND EXIT VALID POSITIONS ####
			self.databaseManager.write('books', 'addToOrderBook', filledEntryOrder)
			self.databaseManager.write("statistics", "updateCapitalStatistics", potentialPositionEntry)
			self.databaseManager.execute('trading', 'exitValidPositions', stratVerdict)
			filledExitOrders, completedPositions = self.databaseManager.processTasks()
			potentialExitMade = bool(potentialPositionEntry or filledExitOrders != [None])

			#### HOUSEKEEPING, LOGGING FINISHED POSITIONS & ORDERS
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

		if endCode == SOFT_EXIT: 
			try:
				self.logger.addEvent('system', "SOFT_EXIT INITIATED. ALL ONGOING TRADES BEING FINALIZED.")
				while (self.databaseManager.classDict['trading'].getCacheSize() > 0):
					self.runSystemLogic()

			except BaseException as e:
				from .Utilities import getStackTrace
				stackTrace = getStackTrace(e)
				self.logger.addEvent('system', ('SOFT_EXIT_FAILURE: ' + str(e)))
				self.logger.addEvent('system', ('SOFT_EXIT_FAILURE_STACKTRACE: ' + str(stackTrace)))

		if endCode == HARD_EXIT:
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
