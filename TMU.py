import Position as pmu 
import Constants as cst
import Order as omu 

class TMU(object):

	def __init__(self, tradingType):
		
		self.TLU_VERDICT = cst.NOT_SET
		self.orderQueue = omu.OrderQueue(tradingType)
		self.positionCache = pmu.PositionCache()

	def updateTLU(self, updatedTLU):
		self.TLU_VERDICT = updatedTLU.getPos()

	def placeOrder(self, ticker, quantity):

		if (not self.TLU_VERDICT == 0):

			if (self.orderQueue.tradingMode == "BT"):
				newOrder = omu.Order(self.TLU_VERDICT, ticker, quantity)
				self.orderQueue.enqueue(newOrder)

			if (self.orderQueue.tradingMode == "RT"): pass

	def onCurrentTick(self, updatedTLU, portfolio, currentTime): 
		
		self.updateTLU(updatedTLU)
		if (self.TLU_VERDICT == 0): return cst.CURRENT_TICK_HOLD
		
		if (self.TLU_VERDICT == 1): # temporary, must support both long/short
			for unit in portfolio.units:
				self.placeOrder(unit.ticker, unit.quantity)

		orderList = self.orderQueue.fillPlacedOrders()

		if (orderList != []):
			self.positionCache.addPositions(orderList, currentTime)
			
		exitPositionsList = self.positionCache.checkCache(self.TLU_VERDICT)
		if (exitPositionsList == []): return cst.NO_EXIT_POSITIONS

		return self.positionCache.exitPositions(exitPositionsList, currentTime)

