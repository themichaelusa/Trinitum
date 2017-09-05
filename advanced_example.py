from Trinitum import Gem

def entryConditions(data): 
	aroonup, aroondown = data['AROON']
	validEntry = data['price'] < data['EMA'] and aroondown >= 80
	if (validEntry): return 1
	else: return 0

def exitConditions(data):
	aroonup, aroondown = data['AROON'] 
	validExit = data['price'] > data['EMA'] and aroonup >= 80
	if (validExit): return 1
	else: return 0

key, secret, passphrase = 'blah', 'bloo', 'blee'

gem = Gem('ADVANCED', 'BTC-USD', quantity=.01)
gem.addStrategy('S1', entryConditions, exitConditions)
gem.addIndicator('AROON', 10), gem.addIndicator('MA', 5, 1)

gem.addExchangeCredentials('GDAX', key, passphrase, secret)
gem.addRiskParameters(poslimit=1, tolerance=.05)
gem.addAdvancedParameters(indicatorLag=150, systemLag=2)
gem.run(endTime='20170910')
