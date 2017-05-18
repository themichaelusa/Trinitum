
"""
Trading Universe

Objective: 
1. Define Trading Universe (Cryptocurrency Options/Futures, Stock Options/Futures, etc.)
2. For Each Unit (Ticker/Currency, Quantity, Priority (0-100))
"""

class Unit(object):
	
	def __init__(self, ticker, quantity, priority = None):
		
		self.ticker = ticker
		self.quantity = quantity
		self.priority = priority
		
class Portfolio(object):

	def __init__(self):
		self.units = []

	def addUnit(self, ticker, quantity, priority):

		self.units.append(Unit(ticker, quantity, priority))
		self.units.sort(key=lambda u: u.priority, reverse=True)

	def addUnitDict(self, unitDict): pass
