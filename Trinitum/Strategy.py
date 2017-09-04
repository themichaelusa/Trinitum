class Strategy(object):

	def __init__(self, ID, entryStrat, exitStrat):
		
		self.ID = ID
		self.entryStrat = entryStrat
		self.exitStrat = exitStrat

	def setStopLoss(self, price, trailing = False): pass

	def tryEntryStrategy(self, tickData): 
		return self.entryStrat(tickData)

	def tryExitStrategy(self, pCacheSize, tickData): 
		if (pCacheSize > 0): 
			return self.exitStrat(tickData)
		else: return 0

