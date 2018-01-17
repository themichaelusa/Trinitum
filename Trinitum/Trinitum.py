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

	def __init__(self, name, symbol, quantity, sandbox=False):
		self.name, self.symbol, self.quantity = name, symbol, quantity
		self.exchange, self.key, self.password, self.secret = (None,)*4
		self.strategy, self.profile = (None,)*2
		self.histInterval, self.histPeriod = (300,)*2
		self.indicators = {}

		from .Constants import DEFAULT_IND_LAG, DEFAULT_SYS_LAG
		self.indicatorLag, self.systemLag = DEFAULT_IND_LAG, DEFAULT_SYS_LAG
		self.customLogic, self.customData = None, {}
		self.sandbox = sandbox
		self.runLimit = None

	def addStrategy(self, stratName, stratRef):
		from .Strategy import Strategy
		self.strategy = Strategy(stratName, stratRef)

	def addIndicator(self, indicator, *indArgs):
		self.indicators.update({indicator: indArgs})

	def addRiskProfile(self, rpName, riskRef, params={}):
		from .RiskProfile import RiskProfile
		if params == {}:
			from .Constants import DEFAULT_RISK_PARAMETERS
			self.profile = RiskProfile(rpName, DEFAULT_RISK_PARAMETERS)
		else:
			self.profile = RiskProfile(rpName, params)

		self.profile.riskRef = riskRef

	def addRiskAnalytic(self, name):
		self.profile.addAnalytic(name)

	def setHistDataParams(self, histInterval=300, histPeriod=300):
		self.histInterval, self.histPeriod = histInterval, histPeriod

	def addCustomDataFeed(self, name, ref, *args): 
		if self.sandbox:
			self.customData.update({name: (ref, args)})

	def addCustomSysLogic(self, logic):
		if self.sandbox:
			self.sysLogic = logic

	def setRunLimit(self, times=None):
		self.runLimit = times

	"""
	def importLiveData(self, location="DataBank", name=None): pass
	def importDataSet(self, location="DataBank", name=None): pass
	"""

class Gem(TrinitumInstance):
	
	def __init__(self, name, symbol, quantity, sandbox=False):
		super().__init__(name, symbol, quantity, sandbox)

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

	def run(self, endTime, endCode=0):
		from .TradingInstance import TradingInstance
		tri = TradingInstance(self.name, self.strategy, self.profile)
		endTime = endTime.replace('/', '')
		
		tri.setExchangeAuthCredentials(self.key, self.secret, self.password)
		tri.setSymbol(self.exchange, self.symbol, self.quantity)
		tri.setLagParams(self.indicatorLag, self.systemLag)
		tri.createLoggerInstance((self.name + 'syslog'))

		tri.start(endTime, self.histInterval, self.histPeriod, self.indicators.items())
		tri.run(endTime, endCode, self.runLimit)	
	
class Template:
	@staticmethod
	def generate(): pass
				