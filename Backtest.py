import Position as pmu 
import CONST as cst
import UTILS as utl
import Order as omu 
import TLU as tlu
import TMU as tmu

class Backtest(object):

	def __init__(self, data, portfolio, strategy, capital = 100000, commision = .01):
		
		self.data = data
		self.portfolio = portfolio
		self.strategy = strategy

		self.capital = capital
		self.commision = commision

	def addStopLoss(self, ticker, upperlower, trailing): pass
	def exportAdditionalDiagnostics(self, exportBool): pass

	def run(self, startDate, endDate): 

		backtestTMU = tmu.TMU("BT")
		backtestTMU.updateTLU(cst.INIT_TMU)
		allTLUResults = [tlu.TLU(tickData, self.strategy) for tickData in self.data]

		for currentTLU in allTLUResults:

			currentTime = utl.getCurrentTime() # temporary
			currentTick = backtestTMU.onCurrentTick(currentTLU, currentTime)
