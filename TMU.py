import Position as pmu 
import CONST as cst
import UTILS as utl
import Order as omu 
import TLU as tlu

class TMU(object):

	def __init__(self, currentTLU, orderQueue, positionCache):
		
		self.TLU_VERDICT = currentTLU.getPos()
		self.orderQueue = orderQueue
		self.positionCache = positionCache

	def updateTLU(self, updatedTLU):
		self.TLU_VERDICT = updatedTLU.getPos()

	def onCurrentTick(self, newTLU, currPrice, currTime, ticker = None, quantity = None): 
		
		self.updateTLU(newTLU)
		if (ticker != None and quantity != None):
			self.placeOrder(ticker, quantity)

		orderList = self.orderQueue.fillPlacedOrders()
		exitPositionTuple = self.positionCache.checkCache(newTLU)
		
		if (exitPositionTuple == False or len(orderList) == 0): 
			pass
		
		else: 
			exitPos, exitPosIndex = exitPositionTuple[0], exitPositionTuple[1]
			exitPos.setExitParams(currPrice, currTime)
			self.positionCache.removePosition(exitPosIndex)
			# du.addToPositionBook(exitPos)
			return exitPos

	def placeOrder(self, ticker, quantity):

		if (not self.TLU_VERDICT == 0):

			if (self.orderQueue.tradingMode == "BT"):
				newOrder = omu.Order(self.TLU_VERDICT, ticker, quantity)
				self.orderQueue.enqueue(newOrder)

			if (self.orderQueue.tradingMode == "RT"): 
				pass

def buy(data): 
	if (data[0] == 0): return 1
	else: return 0

def sell(data): 
	if (data[0] == 1): return 1
	else: return 0

data, newData = (0, 1), (1,1)
blocks = (buy, sell)
rules = ('10', '01', '00')

strat = tlu.Strategy(blocks, rules)
testTLU = tlu.TLU(data, strat)
testOQ = omu.OrderQueue("BT")
testPC = pmu.PositionCache()
testTMU = TMU(testTLU, testOQ, testPC)

testTMU.placeOrder("AMD", 100)
testTMU.placeOrder("GM", 44)
testTMU.placeOrder("TSLA", 987)
testTMU.placeOrder("NVDA", 12)

orderList = testTMU.orderQueue.fillPlacedOrders()
testTMU.positionCache.addPositions(orderList, utl.getCurrentTime())
print(testTMU.positionCache.checkCache(1))

