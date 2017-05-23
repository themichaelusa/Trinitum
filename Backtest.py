import Portfolio as pfl
import Position as pmu 
import CONST as cst
import UTILS as utl
import Order as omu 
import TLU as tlu
import TMU as tmu

import pandas as pd

class Backtest(object):

	def __init__(self, data, portfolio, strategy, capital = 100000, commision = .01):
		
		self.data = data
		self.portfolio = portfolio
		self.strategy = strategy

		self.capital = capital
		self.commision = commision
		# self.positionsToLog = []

	def addStopLoss(self, ticker, value, trailing): pass
	def exportAdditionalDiagnostics(self): pass

	def run(self, startDate, endDate): 

		backtestTMU = tmu.TMU("BT")
		backtestTMU.updateTLU(cst.INIT_TMU)
		allTLUResults = (tlu.TLU(tickData, self.strategy) for tickData in self.data)

		def onCurrentTickWrapper(portf, currTLU):

			currentTime = utl.getCurrentTime()
			return backtestTMU.onCurrentTick(currTLU, portf, currentTime)
		
		positionsToLog = [onCurrentTickWrapper(self.portfolio, cTLU) for cTLU in allTLUResults]
		#filteredPositions = 


