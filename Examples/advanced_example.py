from Trinitum import Gem

def myAROON(data):
	aroonup, aroondown = data['AROON']
	if (data['price'] < data['EMA'] and aroondown >= 80): return 1
	if (data['price'] > data['EMA'] and aroonup >= 80): return -1

key, secret, passphrase = 'blah', 'bloo', 'blee'

gem = Gem('ADVANCED', 'BTC-USD', quantity=.01)
gem.addStrategy('S1', myAROON)
gem.addIndicator('AROON', 10), gem.addIndicator('MA', 5, 1)

gem.addExchangeCredentials('GDAX', key, passphrase, secret)
gem.addRiskParameters(poslimit=1, tolerance=.05)
gem.addAdvancedParameters(indicatorLag=150, systemLag=2)
gem.run(endTime='20170910', endCode=0)
