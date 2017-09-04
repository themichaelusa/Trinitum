from TradingInstance import TradingInstance
from Strategy import Strategy

""" 
Welcome to the Trinitum Instance. 
Struture of the System by Hierarchy: 

1. Trinitum.py
2. TradingInstance.py
3. DatabaseManager.py
4. AsyncManager.py

When a user initializes a Gem class, they are just using a fancy wrapper
for the TradingInstance class. After a user adds all the mandatory 
parameters (addStrategy, addExchangeCredentials) and any optional 
parameters (addIndicator, setHistDataParams, addRiskParameters,
addAdvancedParameters), the user calls the run method.
This organizes all the entered fields to something TradingInstance
understands. 

All the methods below are setters. Now, go to #2 to learn more about 
how the system actually trades.
"""

class TrinitumInstance(object):

	def __init__(self, name, symbol, quantity):
		
		self.name, self.symbol, self.quantity = name, symbol, quantity
		self.stratName, self.entryConds, self.exitConds = (None,)*3
		self.inds = {}

		self.exchange, self.key, self.password, self.secret = (None,)*4
		self.histInterval, self.histPeriod = (300,)*2
		self.indicatorLag, self.systemLag = (1,)*2
		self.tolerance = .05
		self.poslimit = 1

		self.gemResults = None

	def addIndicator(self, indicator, *indArgs):
		self.inds.update({indicator: indArgs})

	def addStrategy(self, stratName, entryConds, exitConds):
		self.stratName, self.entryConds, self.exitConds = stratName, entryConds, exitConds

	def setHistDataParams(self, histInterval=300, histPeriod=300):
		self.histInterval, self.histPeriod = histInterval, histPeriod
		
class Gem(TrinitumInstance):
	
	def __init__(self, name, symbol, quantity):
		super().__init__(name, symbol, quantity)

	def addExchangeCredentials(self, exchange, key=None, password=None, secret=None):
		self.exchange, self.key, self.password, self.secret = exchange, key, password, secret

	def addRiskParameters(self, poslimit=1, tolerance=.05):
		self.poslimit, self.tolerance = poslimit, tolerance

	def addAdvancedParameters(self, indicatorLag=1, systemLag=1):
		self.indicatorLag, self.systemLag = indicatorLag, systemLag

	def run(self, endTime, endCode=0):

		tri = TradingInstance(self.name)
		tri.setExchangeAuthCredentials(self.key, self.secret, self.password)
		tri.setSymbol(self.exchange, self.symbol, self.quantity)
		tri.setTradingParams(self.inds, self.tolerance, self.poslimit)
		tri.setLagParams(self.indicatorLag, self.systemLag)
		tri.createLoggerInstance((self.name + 'syslog'))
		tri.start(self.stratName, self.entryConds, self.exitConds)
		self.gemResults = tri.run(endTime, self.histInterval, self.histPeriod, endCode)	
		