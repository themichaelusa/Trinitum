# Trinitum
![help](https://github.com/themichaelusa/Trinitum/blob/master/assets/logo.png)
Algorithmic cryptocurrency trading in as little as 10 lines of Python. USE AT YOUR OWN RISK. 

## Installation
```
pip3 install trinitum
brew install rethinkdb
```

## Documentation

### Basic Example:

```python
from Trinitum import Gem

def myFirstStrategy(data):
	if (data['RSI'] >= 30 and data['RSI'] <= 50): return 1
	if (data['RSI'] >= 70): return -1

gem = Gem('BASIC', 'BTC-USD', quantity=.01)
gem.addStrategy('S1', myFirstStrategy)
gem.addIndicator('RSI', 10)

key, secret, passphrase = 'blah', 'bloo', 'blee'
gem.addExchangeCredentials('GDAX', key, passphrase, secret)
gem.run(endTime='20170910')
```
### Advanced Example:

```python
from Trinitum import Gem

def myAROON(data):
	aroonup, aroondown = data['AROON']
	if (data['price'] < data['EMA'] and aroondown >= 80): return 1
	if (data['price'] > data['EMA'] and aroonup >= 80): return -1

gem = Gem('ADVANCED', 'BTC-USD', quantity=.01)
gem.addStrategy('S1', myAROON)
gem.addIndicator('AROON', 10)
gem.addIndicator('MA', 5, 1)

key, secret, passphrase = 'blah', 'bloo', 'blee'
gem.addExchangeCredentials('GDAX', key, passphrase, secret)

gem.addRiskParameters(poslimit=1, tolerance=.05)
gem.addAdvancedParameters(indicatorLag=150, systemLag=2)
gem.run(endTime='20170910', endCode=0)	
```
## TODO

- [ ] Add support for custom strategy scripts
- [ ] Better Documentation
- [ ] Add Risk Statistics
- [ ] Add VWAP indicator
