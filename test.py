import Backtest as bt
import Portfolio as uni
import Position as pmu 
import Order as omu 
import poloWrapper as pw

import CONST as cst
import UTILS as utl
import TLU as tlu
import TMU as tmu


def buy(data): 
	if (data[0] == 0): return 1
	else: return 0

def sell(data): 
	if (data[0] == 1): return 1
	else: return 0

data = [(0,1), (1,1), (2,2), (2,2), (1,1), (0,1), (2,2), (1,1)]
blocks = (buy, sell)
rules = ('10', '01', '00')
strategy = tlu.Strategy(blocks, rules)

universe = uni.Universe()
universe.addUnit("BTC", 5, 100)
backtest = bt.Backtest(data, universe, strategy, 100000, .01)
results = backtest.run("20170401", "20170516")
print(results)
