class Order(object):
	
	def __init__(self, entryExit = None, direction = None, ticker = None, quantity = None):

		self.oID = None
		self.entryExit = entryExit
		self.direction = direction
		self.ticker = ticker
		self.quantity = quantity
		self.errorCode = None

	def setErrorCode(self, errorCode):
		self.errorCode = errorCode

	def setOrderID(self, oID):
		self.oID = oID
