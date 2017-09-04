from Trinitum import Gem

def entryConditions(stratData): 

	price, volume, upperband, EMA, lowerband = stratData
	if (price <= lowerband): return 1
	else: return 0

def exitConditions(stratData): 

	price, volume, upperband, EMA, lowerband = stratData	
	if (price > EMA or price <= lowerband*.95): return 1
	else: return 0

key = 'blah'
secret = 'bloo'
passphrase = 'blee'

gem = Gem('BBANDS_0001', 'BTC-USD', quantity=.01)
gem.addStrategy('S1', entryConditions, exitConditions)
gem.addIndicator('BBANDS', 10, 2, 2, 1)

gem.addExchangeCredentials('GDAX', key, passphrase, secret)
gem.addRiskParameters(poslimit=1, tolerance=.05)
gem.addAdvancedParameters(indicatorLag=150, systemLag=2)
gem.run(endTime='20170901')
