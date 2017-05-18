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

class Order(object):
	
	def __init__(self, orderType, ticker, quantity):
		
		self.ID = str(uuid4())
		self.orderType = orderType
		self.ticker = ticker
		self.quantity = quantity

class OrderQueue(object):

    def __init__(self, tradingMode):
        
        self.orders = []
        self.tradingMode = tradingMode
        # self.mmuData = mmu.getFeed() 

    def fillPlacedOrders(self): 
        
        if (self.tradingMode == "BT"):
            return [self.dequeue() for i in range(self.size())]

        if (self.tradingMode == "RT"): pass

    def isEmpty(self):
        return self.orders == []

    def enqueue(self, item):
        self.orders.append(item)

    def dequeue(self):
    	
        if (self.tradingMode == "BT"):
            return self.orders.pop()

        if (self.tradingMode == "RT"): pass

    def size(self):
        return len(self.orders)
	