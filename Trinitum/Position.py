class Position(object):

	def __init__(self, ID = None, direction = None, ticker = None, quantity = None, entryPrice = None, entryTime = None):
		
		self.entID = ID
		self.direction = direction
		self.ticker = ticker
		self.quantity = quantity
		self.entryPrice = float(entryPrice)
		self.entryTime = entryTime

		self.exID = cst.NOT_SET
		self.exitPrice = cst.NOT_SET
		self.exitTime = cst.NOT_SET
		self.returns = cst.NOT_SET
		self.tradingWindow = cst.NOT_SET
		self.gain = cst.NOT_SET

	def setExitID(self, exID):
		self.exID = exID
		
	def setExitParams(self, exitPrice, exitTime):

		self.exitPrice = float(exitPrice)
		self.exitTime = exitTime

		self.gain = self.exitPrice - self.entryPrice
		percentReturn = self.exitPrice/self.entryPrice
		if (percentReturn >= 1): self.returns = percentReturn
		else: self.returns = -1*percentReturn 
