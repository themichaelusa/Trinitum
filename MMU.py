
"""
Money Management Unit

Objective: 
1. Retrieve Information Regarding Capital (Current Balance, Current Orders, Commission)
2. Deposit Module (Offload Portion of Profits with API's to Coinbase/Prosper/Bank Accts(Stripe))
3. Risk Management (With Kelly Criterion) && Calculate Positional Probabilities
4. Deposit Module (Offload Portion of Profits with API's to Coinbase/Prosper/Bank Accts(Stripe))
"""

import poloWrapper

class MMU(object):
	def __init__(self, APIKey, Secret):
		self.APIKey = APIKey
        self.Secret = Secret
        self.polo = poloWrapper(self.APIKey,self.secret)

    def getBalance():
        return self.polo.returnBalances()

    def getCurrentOrders():
        return self.polo.returnOpenOrders("all")

    def getCommission():
        'based on Universe, will add when universe.py is done
        pass

    def deposit():
        'need actual account address, but pretty simple, will just call withdraw from the polniex API wrapper
        pass
class Deposit(object):
	def __init__(self, arg):
		self.arg = arg


