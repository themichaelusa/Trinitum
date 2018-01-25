class Strategy(object):

	def __init__(self, ID, tradeRef):
		self.ID = ID
		self.tradeRef = tradeRef
		self.riskRef = None

	def tryTradeStrategy(self, tickData): 
		result = self.tradeRef(tickData)
		if (result is None): return 0
		else: return result

	def tryRiskStrategy(self, riskData):
		result = self.riskRef(riskData)
		if (result is None): return 0
		else: return result
