class Strategy(object):

	def __init__(self, ID, stratRef):
		self.ID = ID
		self.stratRef = stratRef

	def tryStrategy(self, tickData): 
		result = self.stratRef(tickData)
		if (result is None): return 0
		else: return result

	def setStopLoss(self, price, trailing = False): pass


