import time
import asyncio
import rethinkdb as r

class AsyncTaskManager(object):

	def __init__(self, dbReference, connection, logger): 
		
		self.funcDict = {}
		self.connection = connection
		self.dbReference = dbReference
		self.logger = logger

	def setFunctionDict(self, newDict):
		self.funcDict = newDict

	def pullTableContents(self, tableRef):
		contents = tableRef.run(self.connection)
		return [data for data in contents]

class AsyncPipelineManager(AsyncTaskManager):

	def __init__(self, dbReference, connection, logger): 		

		super().__init__(dbReference, connection, logger)
		from .Pipeline import Formatter
		from gdax import PublicClient

		self.formatter = Formatter()
		self.gdaxPublicClient = PublicClient()
		self.symbol, self.techInds, self.spotInds, self.spotCustom = (None,)*4
	
		from .Constants import DEFAULT_SPOT_DATA_DICT, DEFAULT_CUSTOM_DATA
		self.spotData = DEFAULT_SPOT_DATA_DICT
		self.customDataFeeds = DEFAULT_CUSTOM_DATA

	async def updateSpotData(self): #write
		try:
			spotData = dict(self.gdaxPublicClient.get_product_ticker(self.symbol))
			self.spotData['price'] = float(spotData['price'])
			self.spotData['volume']	= float(spotData['volume'])

		except BaseException as e: 
			self.logger.addEvent('trading', ('UPDATE_SPOT_DATA_ERROR: ' + str(e)))

		await asyncio.sleep(0)

	async def updateTechIndicators(self, lag=1): #write
		try:
			OHLCV = list(self.gdaxPublicClient.get_product_24hr_stats(self.symbol).values())[:3]
			OHLCV = [float(data) for data in OHLCV]
			OHLCV.extend([self.spotData['price'], self.spotData['volume']])

			for ind in self.techInds:
				self.spotInds[ind.tbWrapper.indicator] = ind.getRealtime(OHLCV, lag)
			
		except BaseException as e: 
			self.logger.addEvent('trading', ('UPDATE_TECH_INDS_ERROR: ' + str(e)))

		await asyncio.sleep(0)

	async def runCustomDataFeeds(self):
		complete = {}
		for name, ref, args in zip(self.customDataFeeds.items()): 
			result = ref(*args)
			complete.update({name: result})
		self.spotCustom = complete
		await asyncio.sleep(0)

	async def getPipelineData(self): #read
		formattedStratData = self.formatter.formatStratData(self.spotData, self.spotInds, self.spotCustom)
		await asyncio.sleep(0)
		return formattedStratData

class AsyncStrategyManager(AsyncTaskManager):
	
	def __init__(self, dbReference, connection, logger): 		
		super().__init__(dbReference, connection, logger)
		self.strategy = None

	async def tryEntryStrategy(self, tickData, riskData): #execute
		tradeResult = self.strategy.tryTradeStrategy(tickData) 
		riskResult = self.strategy.tryRiskStrategy(riskData)

		if (tradeResult == 1 and riskResult == 1): 
			self.logger.addEvent('strategy', 'POSITION ENTRY CONDITIONS VALID')
		
		await asyncio.sleep(0)
		return tradeResult

	"""
	async def tryExitStrategy(self, tickData, targetPos, pCacheSize): #execute
		tradeResult = self.strategy.tryTradeStrategy(tickData) 
		
		if (tradeResult == -1 and pCacheSize > 0):
			self.logger.addEvent('strategy', 'POSITION EXIT CONDITIONS VALID')

		await asyncio.sleep(0)
		return tradeResult
	"""

class AsyncStatisticsManager(AsyncTaskManager):

	def __init__(self, dbReference, connection, authData, logger): 		
		super().__init__(dbReference, connection, logger)
		from gdax import AuthenticatedClient
		self.gdaxAuthClient = AuthenticatedClient(*authData)

		from .Constants import DEFAULT_CAPITAL_DICT
		self.capitalStats = DEFAULT_CAPITAL_DICT
		self.riskStats, self.riskProfile = (None,)*2
		self.positionBookRef = self.dbReference.table('PositionBook')

	def getReturns(self): 
		positionBook = self.pullTableContents(self.positionBookRef)
		positionBook = positionBook[1:]
		return [p.returns for p in positionBook if p.returns != None]

	async def updateRiskStatistics(self):
		from .Pipeline import getRiskFreeRate
		self.riskProfile.updateRiskFree(getRiskFreeRate())
		self.riskProfile.updateReturns(getReturns())
		
		self.riskStats = self.riskProfile.getAnalytics()
		await asyncio.sleep(0)

	async def updateCapitalStatistics(self, logCapital=False):

		try:	
			accountData = list(self.gdaxAuthClient.get_accounts())
			acctDataUSD = list(filter(lambda x: x['currency'] == "USD", accountData))
			availibleCapitalUSD = float(acctDataUSD[0]['available'])
			printCapitalValid = bool(logCapital == True)
			
			if(printCapitalValid):
				capitalCheck = "Current Capital: " + str(availibleCapitalUSD)
				self.logger.addEvent('statistics', capitalCheck)
			self.capitalStats['capital'] = availibleCapitalUSD

		except BaseException as e: 
			self.logger.addEvent('trading', ('GDAX_AUTHCLIENT_GET_ACCOUNTS_ERROR: ' + str(e)))

		await asyncio.sleep(0)

	def getRiskStats(self, pullRiskParams=False): 
		if pullRiskParams:
			return self.riskStats, self.riskProfile.parameters
		else:
			return self.riskStats

	def getCapitalStats(self): 
		return self.capitalStats
	
class AsyncTradingManager(AsyncTaskManager):

	def __init__(self, dbReference, connection, authData, logger): 		
		super().__init__(dbReference, connection, logger)
		self.positionCache = {}
		from .Constants import NOT_SET
		self.symbol, self.quantity, self.riskParams = (NOT_SET,)*3

		from gdax import AuthenticatedClient
		self.gdaxAuthClient = AuthenticatedClient(*authData)
	
	def getCacheSize(self):
		return self.positionCache.keys().size()

	def validPosLimitCheck(self):
		return bool(self.positionCache.size() <= self.riskParams['posLimit'])

	async def createOrders(self, stratVerdict): #read

		entryOrder = None
		validEntryVerdict = (stratVerdict == 1)

		if (validEntryVerdict and self.validPosLimitCheck()):
			from .Order import Order
			entryOrder = Order('ENTRY', 'B', self.symbol, self.quantity)
			orderLog = "Created Order for: " + str(self.symbol) + " at size: " + str(self.quantity)
			self.logger.addEvent('trading', orderLog)

		await asyncio.sleep(0)
		return entryOrder

	async def verifyAndEnterPosition(self, entryOrder, currentCapital, spotPrice): #read

		newPosition = None
		validEntryConditions = entryOrder is not None and currentCapital > 0

		if validEntryConditions: 
			fundToleranceAvailible = currentCapital*self.riskParams['tolerance'] > self.quantity			
			if (fundToleranceAvailible and self.validPosLimitCheck()):

				response = dict(self.gdaxAuthClient.buy(product_id=self.symbol, type='market', funds=self.quantity)) 
				orderID = response['id']
				time.sleep(1)
				orderStatus = dict(self.gdaxAuthClient.get_order(orderID))
				
				if (orderStatus['status'] != 'done'):
					timedOut = 'TIMED_OUT'
					self.gdaxAuthClient.cancel_order(orderID)
					entryOrder.setErrorCode(timedOut)
					orderTimeOut = 'Order: ' + str(orderID) + ' ' + timedOut
					self.logger.addEvent('trading', orderTimeOut)

				else:
					noErrors = 'NO_ERRORS'
					entryOrder.setOrderID(orderID)
					entryOrder.setErrorCode(noErrors)
					orderFillTime = orderStatus['done_at']
					entryValue = float(response['executed_value'])
					orderData = (entryOrder.direction, self.symbol, self.quantity, entryValue, orderFillTime)
					
					### CREATE POSITION OBJECT FROM ORDERDATA AND ADD TO POSTION CACHE
					from .Position import Position
					newPosition = Position(orderID, *orderData)
					self.positionCache.update({orderID: newPosition})
					positionEntered = noErrors + ', Entered Position: ' + str(orderID)
					self.logger.addEvent('trading', positionEntered)

			else: 
				noFunds = "CAPITAL_TOLERANCE_EXCEEDED"
				entryOrder.setErrorCode(noFunds)
				self.logger.addEvent('trading', noFunds)

		await asyncio.sleep(0)
		return ([entryOrder], newPosition)

	async def exitValidPositions(self, stratVerdict): #read

		#positionCache = self.pullTableContents(self.pCacheRef)
		#validExitConditions = stratVerdict == -1 and positionCache != []
		pCacheSize = self.getCacheSize()
		validExitConditions = stratVerdict == -1 and pCacheSize > 0
		completedPositions, exitOrders = [None], [None]

		if validExitConditions:

			self.logger.addEvent('strategy', 'POSITION EXIT CONDITIONS VALID')
			sellResponses, completedPositions, exitOrders, response = [], [], [], None
			self.gdaxAuthClient.cancel_all(product=self.symbol)
			from .Position import Position
			from .Order import Order

			for p in self.positionCache.values():

				from .Constants import GDAX_FUNDS_ERROR
				while (response == GDAX_FUNDS_ERROR or response == None):
					response = dict(self.gdaxAuthClient.sell(product_id=self.symbol, type='market', funds=self.quantity))
					if (response == GDAX_FUNDS_ERROR):
						self.logger.addEvent('trading', 'INVALID_SELL_RESPONSE: GDAX_FUNDS_ERROR')

				pArgs = (p['entID'], p['direction'], p['ticker'], p['quantity'], p['entryPrice'], p['entryTime'])
				completedPosition = Position(*pArgs)
				completedPosition.setExitID(response['id'])
				completedPositions.append(completedPosition)
				sellResponses.append(response)

				exitOrder = Order('EXIT', 'S', self.symbol, self.quantity)
				exitOrder.setErrorCode("NO_ERRORS")
				exitOrder.setOrderID(response['id'])
				exitOrders.append(exitOrder)
				response = None

			#time.sleep(1)
			self.positionCache.clear()

			for posit, response in zip(completedPositions, sellResponses):
				
				exitedPos = "Exited Position:" + posit.exID
				self.logger.addEvent('trading', exitedPos)

				try:
					orderStatus = dict(self.gdaxAuthClient.get_order(posit.exID))
					orderExitTime = orderStatus['done_at']
					posit.setExitParams(float(response['executed_value']), orderExitTime)
				except BaseException as e: 
					self.logger.addEvent('trading', ('GDAX_AUTHCLIENT_GETORDER_ERROR: ' + str(e)))

			self.pCacheRef.delete().run(self.connection)			
		
		await asyncio.sleep(0)
		return (exitOrders, completedPositions)

	"""
	async def addToPositionCache(self, position): #write

		if (position is not None):
			from .Utilities import getObjectDict
			pDict = getObjectDict(position)
			self.pCacheRef.insert(pDict).run(self.connection)
		
		await asyncio.sleep(0)
	"""

class AsyncBookManager(AsyncTaskManager):
	
	def __init__(self, dbReference, connection, logger):
		
		super().__init__(dbReference, connection, logger)
		self.orderBookRef = self.dbReference.table('OrderBook')
		self.posBookRef = self.dbReference.table("PositionBook")

	async def addToOrderBook(self, orderObjs): #write
		
		if (orderObjs != [None]):
			from .Utilities import getObjectDict
			for orderObj in orderObjs:
				oDict = getObjectDict(orderObj)
				self.orderBookRef.insert(oDict).run(self.connection)

		await asyncio.sleep(0)

	async def addToPositionBook(self, positions): #write

		if (positions != [None]):
			from .Utilities import getObjectDict
			for position in positions:
				pDict = getObjectDict(position)
				self.posBookRef.insert(pDict).run(self.connection)
			
		await asyncio.sleep(0)

	async def getOrderBook(self): #read
		orderBook = self.pullTableContents(self.orderBookRef)
		await asyncio.sleep(0)
		return orderBook

	async def getPositionBook(self): #read
		positionBook = self.pullTableContents(self.posBookRef)
		await asyncio.sleep(0)
		return positionBook

	"""
	async def getReturns(self): #read
		positionBook = self.pullTableContents(self.posBookRef)
		positionBook = positionBook[1:]
		returns = [p.returns in positionBook if p.returns != None]
		await asyncio.sleep(0)
		return returns
	"""
