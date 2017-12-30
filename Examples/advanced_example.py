from Trinitum import Gem

"""
def myAROON(data):
	aroonup, aroondown = data['AROON']
	if (data['price'] < data['EMA'] and aroondown >= 80): return 1
	if (data['price'] > data['EMA'] and aroonup >= 80): return -1

def riskProfile(data):
	remainingFunds = data['FUNDS']
	if (data["SHARPE_RATIO"] > 1 && data['MAX_DRAWDOWN'] < .02*remainingFunds): 
		return 1

gem = Gem('ADVANCED', 'BTC-USD', quantity=.01)
gem.addStrategy('S1', myAROON)
gem.addRiskProfile(riskProfile)
gem.addIndicator('AROON', 10), gem.addIndicator('MA', 5, 1)

riskParameters = {
"posLimit": 1, #num
"tolerance": .05, #pct
"trailingStop": .02, #pct
'resetRiskProfile': 5 #days
}

key, secret, passphrase = 'blah', 'bloo', 'blee'
gem.addExchangeCredentials('GDAX', key, passphrase, secret)
gem.addRiskParameters(riskParameters)
gem.addAdvancedParameters(indicatorLag=150, systemLag=2)
gem.run(endTime='20170910', endCode=0)
"""