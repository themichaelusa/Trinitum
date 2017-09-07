from Trinitum import Gem

def entryConditions(data): 
	if (data['RSI'] >= 30 and data['RSI'] <= 50): return 1
	else: return 0

def exitConditions(data): 
	if (data['RSI'] >= 70): return 1
	else: return 0

key, secret, passphrase = 'blah', 'bloo', 'blee'
gem = Gem('BASIC', 'BTC-USD', quantity=.01)
gem.addStrategy('S1', entryConditions, exitConditions)
gem.addIndicator('RSI', 10)

gem.addExchangeCredentials('GDAX', key, passphrase, secret)
gem.run(endTime='20170910')

