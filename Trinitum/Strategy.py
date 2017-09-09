class Strategy(object):

	def __init__(self, ID, stratRef):
		self.ID = ID
		self.stratRef = stratRef

	def tryStrategy(self, tickData): 
		return self.stratRef(tickData)

	def setStopLoss(self, price, trailing = False): pass


