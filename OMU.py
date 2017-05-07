from datetime import datetime
from uuid import uuid4
import CONST as cst

"""
Order Management Unit

Inputs:
1. TLU Output (-1/0/1)
2. MMU Feed (Universe, Current Capital, Risk Tolerance(Kelly Criterion))

Outputs:
Order Object (Unique ID, Position, Entry Time, Entry Price, Exit Time, Finished?)
"""

class OMU(object):

	def __init__(self, TLU_INPUT, MMU_FEED):
		
		self.entryPosition = TLU_INPUT
		self.exitPosition = None # from TLU will return 0(HOLD)/1(EXIT)
		self.mmuData = MMU_FEED
		self.orderCache = []
		# self.tradingType = mmu.getType()

	class Order(object):
		
		def __init__(self, position):
			
			self.ID = str(uuid4())
			self.position = position
			self.exitPrice = cst.NOT_SET
			self.exitTime = cst.NOT_SET			

	class BT_Order(Order):

		def __init__(self, position, entryPrice, entryTime):
			
			super().__init__(ID, position, exitPrice, exitTime)
			self.entryPrice = entryPrice
			self.entryTime = entryTime

	class RT_Order(Order):

		def __init__(self, position):

			super().__init__(ID, position, exitPrice, exitTime)
			self.entryPrice = plu.getSpotPrice()
			self.EntryTime = str(datetime.now())

	def createOrder(self, entryPrice = None, entryTime = None):

		if (self.tradingType == "BT"):
			self.orderCache.append(BT_Order(self.position, entryPrice, entryTime))

		elif (self.tradingType == "RT"):
			self.orderCache.append(RT_Order(self.position))

	def checkOrderCache(self):

		for i in range(len(self.orderCache)):

			currentOrder = self.orderCache[i]
			if (self.exitPosition != currentOrder.exitPosition):
				self.exitOrder(currentOrder, i)

	def exitOrder(self, currentOrder, index):

		if (self.tradingType == "BT"):

			currentOrder.exitPrice = 
			currentOrder.exitTime = 

			dm.pushOrderData(currentOrder)
			del self.orderCache[index]

		elif (self.tradingType == "RT"):

			currentOrder.exitPrice = plu.getSpotPrice()
			currentOrder.exitTime = str(datetime.now())
			
			dm.pushOrderData(currentOrder)
			del self.orderCache[index]




			
		
