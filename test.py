import Backtest as bt
import Universe as uni
import Position as pmu 
import Order as omu 
import poloWrapper as pw
import talibWrapper as tbw

import CONST as cst
import Utilities as utl
import TLU as tlu
import TMU as tmu
import PLU as plu
import Utilities as utl

def buy(data): 

	btcData, upperBand, middleBand, lowerBand = data
	if (btcData['close'] <= lowerBand): return 1
	else: return 0

def sell(data): 

	btcData, upperBand, middleBand, lowerBand = data
	if (btcData['close'] >= middleBand): return 1
	else: return 0

blocks = (buy, sell)
rules = ('10', '01', '00')
strategy = tlu.Strategy(blocks, rules)
universe = uni.Universe()
universe.addUnit("BTC", 5, 100)

histData = universe.generateHistoricalData(300)
#BBANDS_TEST = universe.generateTechnicalIndicator('BBANDS', 600, (1, 2, 2, 2)) 
EMA = universe.generateTechnicalIndicator('MA', 600, (1,2))
data = (histData, EMA)

PLU = plu.PLU(data, universe, "20170401", "20170516", "BT")
PLU.unpackWrappers(universe)
datasets = PLU.generateDatasets()
print(len(datasets))

"""backtest = bt.Backtest(data, universe, strategy, 100000, .01)
backtest.run("20170401", "20170516")"""


"""histTest = plu.HistoricalData("BTC", 300, "20170401", "20170501").histData
init = tbw.generateInputDict(histTest)

tbHistWrappper = tbw.TalibHistWrapper(init, (2,1))
tbHistOutput = tbHistWrappper.getIndicator("MA")
flattenedList = utl.flattenList(tbHistOutput)
extendedList = utl.extendList(flattenedList, 2)
print(extendedList)
#extendedList = [utl.extendList(ind, 2) for ind in tbHistOutput]
#print(extendedList)
"""