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
		self.spotDataRef = self.dbReference.table('SpotData')
		self.techIndsRef = self.dbReference.table('TechIndicators')
		self.spotPrice, self.spotVolume, self.symbol = (None,)*3

	async def updateSpotData(self): #write

		try:
			spotData = dict(self.gdaxPublicClient.get_product_ticker(self.symbol))
			self.spotPrice, self.spotVolume = float(spotData['price']), float(spotData['volume'])
			self.spotDataRef.update(spotData).run(self.connection)		

		except BaseException as e: 
			self.logger.addEvent('trading', ('UPDATE_SPOT_DATA_ERROR: ' + str(e)))

		await asyncio.sleep(0)

	async def updateTechIndicators(self, techIndsList, lag = 1): #write

		try:
			OHLCV = list(self.gdaxPublicClient.get_product_24hr_stats(self.symbol).values())[:3]
			OHLCV = [float(data) for data in OHLCV]
			OHLCV.extend([self.spotPrice, self.spotVolume])

			techIndDict = {}
			for ind in techIndsList:
				techIndDict.update({ind.tbWrapper.indicator: ind.getRealtime(OHLCV, lag)})
			
			self.techIndsRef.update(techIndDict).run(self.connection)

		except BaseException as e: 
			self.logger.addEvent('trading', ('UPDATE_TECH_INDS_ERROR: ' + str(e)))

		await asyncio.sleep(0)

	async def pullPipelineData(self): #read

		sdData = self.pullTableContents(self.spotDataRef)
		tiData = self.pullTableContents(self.techIndsRef)
		formattedStratData = self.formatter.formatStratData(sdData[0], tiData[0])
		
		await asyncio.sleep(0)
		return formattedStratData

class AsyncStrategyManager(AsyncTaskManager):
	
	def __init__(self, dbReference, connection, strat, logger): 		
		
		super().__init__(dbReference, connection, logger)
		self.strategy = strat
		self.tradingRef = self.dbReference.table('PositionCache')

	async def tryStrategy(self, tickData): #read

		result = self.strategy.tryStrategy(tickData)
		
		if (result == 1): 
			self.logger.addEvent('strategy', 'ENTRY CONDS VALID')
		if (result == -1):
			pCacheSize = int(self.tradingRef.count().run(self.connection))
			if (pCacheSize > 0):
				self.logger.addEvent('strategy', 'EXIT CONDS VALID')

		await asyncio.sleep(0)
		return result

class AsyncStatisticsManager(AsyncTaskManager):

	def __init__(self, dbReference, connection, authData, logger): 		
		
		super().__init__(dbReference, connection, logger)
		from gdax import AuthenticatedClient

		self.gdaxAuthClient = AuthenticatedClient(*authData)
		self.RiskStatsRef = self.dbReference.table('RiskData')
		self.CapitalStatsRef = self.dbReference.table('CapitalData')

	async def updateRiskStatistics(self, rsuDict):
		
		self.RiskStatsRef.update(rsuDict).run(self.connection)
		await asyncio.sleep(0)

	async def updateCapitalStatistics(self, logCapital=False):

		try:	
			accountData = list(self.gdaxAuthClient.get_accounts())
			acctDataUSD = list(filter(lambda x: x['currency'] == "USD", accountData))
			availibleCapitalUSD = float(acctDataUSD[0]['available'])
			printCapitalValid = bool(logCapital == True)
			
			capitalDict = {
			'capital': availibleCapitalUSD, 
			"commission": 'None', 
			"return": 'None'
			}

			if(printCapitalValid):
				capitalCheck = "Current Capital: " + str(availibleCapitalUSD)
				self.logger.addEvent('statistics', capitalCheck)

			self.CapitalStatsRef.update(capitalDict).run(self.connection)

		except BaseException as e: 
			self.logger.addEvent('trading', ('GDAX_AUTHCLIENT_GET_ACCOUNTS_ERROR: ' + str(e)))

		await asyncio.sleep(0)

	async def pullRiskStatistics(self): 

		RiskStats = self.pullTableContents(self.RiskStatsRef)
		await asyncio.sleep(0)
		return RiskStats[0]

	async def pullCapitalStatistics(self): 

		CapitalStats = self.pullTableContents(self.CapitalStatsRef)
		await asyncio.sleep(0)
		return CapitalStats[0]
	
class AsyncTradingManager(AsyncTaskManager):

	def __init__(self, dbReference, connection, authData, logger): 		

		super().__init__(dbReference, connection, logger)
		from gdax import AuthenticatedClient
		
		self.pCacheRef = self.dbReference.table('PositionCache')
		self.RiskStatsRef = self.dbReference.table('RiskStats')
		self.CapitalStatsRef = self.dbReference.table('CapitalStats')
		self.gdaxAuthClient = AuthenticatedClient(*authData)

		from .Constants import NOT_SET
		self.symbol, self.quantity, self.tolerance, self.poslimit = (NOT_SET,)*4

		from .Utilities import getObjectDict
		self.getObjectDict = getObjectDict

	def validPosLimitCheck(self):
		return bool((len(self.pullTableContents(self.pCacheRef))+1) <= self.poslimit)

	async def createOrders(self, stratVerdict): #read

		entryOrder = None
		validEntryVerdict = stratVerdict == 1

		if (validEntryVerdict and self.validPosLimitCheck()):
			from .Order import Order
			entryOrder = Order('ENT', 'B', self.symbol, self.quantity)
			orderLog = "Created Order for: " + str(self.symbol) + " at size: " + str(self.quantity)
			self.logger.addEvent('trading', orderLog)

		await asyncio.sleep(0)
		return entryOrder

	async def verifyAndEnterPosition(self, entryOrder, capitalStats, spotPrice): #read

		newPosition, currentCapital = None, capitalStats['capital']
		validEntryConditions = entryOrder is not None and currentCapital > 0

		if (validEntryConditions and self.validPosLimitCheck()): 

			fundToleranceAvailible = currentCapital*self.tolerance > self.quantity
			#check db for viable kelly criterion values, max draw, etc. (not done)
			
			if (fundToleranceAvailible):

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
					
					from .Position import Position
					newPosition = Position(orderID, *orderData)
					positionEntered = noErrors + ', Entered Position: ' + str(orderID)
					self.logger.addEvent('trading', positionEntered)

			else: 
				noFunds = "CAPITAL_TOLERANCE_EXCEEDED"
				entryOrder.setErrorCode(noFunds)
				self.logger.addEvent('trading', noFunds)

		await asyncio.sleep(0)
		return ([entryOrder], newPosition)

	async def exitValidPositions(self, stratVerdict): #read

		positionCache = self.pullTableContents(self.pCacheRef)
		validExitConditions = stratVerdict == -1 and positionCache != []
		completedPositions, exitOrders = [None], [None]

		if (validExitConditions):

			sellResponses, completedPositions, exitOrders, response = [], [], [], None
			self.gdaxAuthClient.cancel_all(product=self.symbol)
			from .Position import Position
			from .Order import Order

			for p in positionCache:

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

				exitOrder = Order('EX', 'S', self.symbol, self.quantity)
				exitOrder.setErrorCode("NO_ERRORS")
				exitOrder.setOrderID(response['id'])
				exitOrders.append(exitOrder)
				response = None

			time.sleep(1)

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

	async def addToPositionCache(self, position): #write

		if (position is not None):
			pDict = self.getObjectDict(position)
			self.pCacheRef.insert(pDict).run(self.connection)
		
		await asyncio.sleep(0)

class AsyncBookManager(AsyncTaskManager):
	
	def __init__(self, dbReference, connection, logger):
		
		super().__init__(dbReference, connection, logger)
		self.orderBookRef = self.dbReference.table('OrderBook')
		self.posBookRef = self.dbReference.table("PositionBook")

		from .Utilities import getObjectDict
		self.getObjectDict = getObjectDict

	async def addToOrderBook(self, orderObjs): #write
		
		if (orderObjs != [None]):
			for orderObj in orderObjs:
				oDict = self.getObjectDict(orderObj)
				self.orderBookRef.insert(oDict).run(self.connection)

		await asyncio.sleep(0)

	async def addToPositionBook(self, positions): #write

		if (positions != [None]):
			for position in positions:
				pDict = self.getObjectDict(position)
				self.posBookRef.insert(pDict).run(self.connection)
			
		await asyncio.sleep(0)

	async def getOrderBook(self): #read

		OrderBook = self.pullTableContents(self.orderBookRef)
		await asyncio.sleep(0)
		return OrderBook

	async def getPositionBook(self): #read
	
		PositionBook = self.pullTableContents(self.posBookRef)
		await asyncio.sleep(0)
		return PositionBook
