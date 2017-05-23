import Portfolio as pfl
import Position as pmu 
import CONST as cst
import Utilities as utl
import Order as omu 
import TLU as tlu
import TMU as tmu

import pandas as pd

class Backtest(object):

	def __init__(self, data, universe, strategy, capital = 100000, commision = .01):
		
		self.data = data
		self.universe = universe
		self.strategy = strategy

		self.capital = capital
		self.commision = commision
		# self.positionsToLog = []

	def addStopLoss(self, ticker, value, trailing): pass
	def exportAdditionalDiagnostics(self): pass

	def run(self, startDate, endDate): 

		backtestTMU = tmu.TMU("BT")		
		backtestTMU.updateTLU(cst.INIT_TMU)
		backtestPLU = plu.PLU(self.data, self.universe, self.universe.frequency, startDate, endDate)
		allTLUResults = (tlu.TLU(tickData, self.strategy) for tickData in self.data)

		def onCurrentTickWrapper(universe, currTLU):

			currentTime = utl.getCurrentTime()
			return backtestTMU.onCurrentTick(currTLU, universe, currentTime)
		
		positionsToLog = [onCurrentTickWrapper(self.universe, cTLU) for cTLU in allTLUResults]
		#filteredPositions = 


