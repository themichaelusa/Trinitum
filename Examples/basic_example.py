from Trinitum import Gem

def myFirstStrategy(data):
	if (data['RSI'] >= 30 and data['RSI'] <= 50): return 1
	if (data['RSI'] >= 70): return -1

key, secret, passphrase = 'blah', 'bloo', 'blee'
gem = Gem('BASIC', 'BTC-USD', quantity=.01)
gem.addStrategy('S1', myFirstStrategy)
gem.addIndicator('RSI', 10)

gem.addExchangeCredentials('GDAX', key, passphrase, secret)
gem.run(endTime='20170910')
