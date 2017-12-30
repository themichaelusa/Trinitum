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
		self.exchange, self.key, self.password, self.secret = (None,)*4
		self.strategy, self.profile = (None,)*2
		self.histInterval, self.histPeriod = (300,)*2

		from .Constants import DEFAULT_IND_LAG, DEFAULT_SYS_LAG
		self.indicatorLag, self.systemLag = DEFAULT_IND_LAG, DEFAULT_SYS_LAG

	def addStrategy(self, stratName, stratRef):
		from .Strategy import Strategy
		self.strategy = Strategy(stratName, stratRef)

	def addIndicator(self, indicator, *indArgs):
		self.strategy.addIndicator(indicator, *indArgs)

	def addRiskProfile(self, rpName, profileRef, params={}):
		from .RiskAnalysis import RiskProfile
		if params == {}:
			from .Constants import DEFAULT_RISK_PARAMETERS
			self.profile = RiskProfile(rpName, profileRef, DEFAULT_RISK_PARAMETERS)
		else:
			self.profile = RiskProfile(rpName, profileRef, params)

	def addRiskAnalytic(self, name):
		self.profile.addAnalytic(name)

	def setHistDataParams(self, histInterval=300, histPeriod=300):
		self.histInterval, self.histPeriod = histInterval, histPeriod

	def importLiveData(self, location="DataBank", name=None): pass

	def importDataSet(self, location="DataBank", name=None): pass

class Gem(TrinitumInstance):
	
	def __init__(self, name, symbol, quantity):
		super().__init__(name, symbol, quantity)

	def addExchangeCredentials(self, exchange, key=None, password=None, secret=None):
		self.exchange, self.key, self.password, self.secret = exchange, key, password, secret

	def addRiskParameters(self, riskParameters=None):
		from .Constants import DEFAULT_RISK_PARAMETERS
		if riskParameters == None:
			self.riskParameters = DEFAULT_RISK_PARAMETERS
		else:
			self.riskParameters = riskParameters

	def addAdvancedParameters(self, indicatorLag=1, systemLag=0):
		self.indicatorLag, self.systemLag = indicatorLag, systemLag

	"""
	def run(self, endTime, endCode=0):
		
		from .TradingInstance import TradingInstance
		tri = TradingInstance(self.name)
		
		tri.setExchangeAuthCredentials(self.key, self.secret, self.password)
		tri.setSymbol(self.exchange, self.symbol, self.quantity)
		tri.setTradingParams(self.inds, self.tolerance, self.poslimit)
		tri.setLagParams(self.indicatorLag, self.systemLag)
		tri.createLoggerInstance((self.name + 'syslog'))
		tri.start(self.stratName, self.stratRef)
		tri.run(endTime, self.histInterval, self.histPeriod, endCode)	
	"""
	
class Template:
	"""
	def __init__(self, arg):
		self.arg = arg
	"""
	@staticmethod
	def generate(): pass
				