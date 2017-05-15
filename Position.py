import CONST as cst
import PLU as plu

class Position(object):

	def __init__(self, ID, posType, ticker, quantity, entryPrice, entryTime):
		
		self.ID = ID
		self.posType = posType
		self.ticker = ticker
		self.quantity = quantity
		self.entryPrice = entryPrice
		self.entryTime = entryTime

		self.exitPrice = cst.NOT_SET
		self.exitTime = cst.NOT_SET

	def setExitParams(self, exitPrice, exitTime):
		self.exitPrice = exitPrice
		self.exitTime = exitTime

class PositionCache(object):

	def __init__(self):
		self.currentPositions = []

	def addPositions(self, orders, entTime):

		ordersValues = [(o.ID, o.orderType, o.ticker, o.quantity, plu.pullSpotPrice(o.ticker)) for o in orders]
		newPositions = [Position(*order, entTime) for order in ordersValues]
		self.currentPositions.extend(newPositions[::-1]) #reversed list

	def checkCache(self, targetPositionType):

		for i in range(len(self.currentPositions)):

			currentPosition = self.currentPositions[i]
			currentPositionType = currentPosition.posType

			if (currentPositionType == 0): continue
			positionSwapped = targetPositionType == currentPositionType*-1

			if (positionSwapped):
				return (currentPosition, i)

			else: 
				return False

	def exitPosition(self, index):

		finishedPosition = self.currentPositions[index]
		del finishedPosition
		return finishedPosition

