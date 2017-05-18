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

	def checkCache(self, TLU_INPUT):

		if (TLU_INPUT == 0): return
		exitPositions = list(filter(lambda x: (x.posType*-1 == TLU_INPUT), self.currentPositions))
		return [ePos.ID for ePos in exitPositions] # returns ID's of positions to be exited

	def exitPositions(self, positionIDS, currentTime):
		
		finishedPositions = list(filter(lambda pos: (pos.ID in positionIDS), self.currentPositions))
		indiciesToRemove = [i for i,x in enumerate(self.currentPositions) if x.ID in positionIDS]

		for index in sorted(indiciesToRemove, reverse=True): #deletes in reverse order, so no-reindexing
			del self.currentPositions[indiciesToRemove[index]]

		for fp in finishedPositions:
			fp.setExitParams(plu.pullSpotPrice(fp.ticker), currentTime)

		return finishedPositions

	