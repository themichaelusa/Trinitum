"""
Money Management Unit

Objective: 
1. Retrieve Information Regarding Capital (Current Balance, Current Orders, Commission)
2. Define Trading Universe (Cryptocurrency Options/Futures, Stock Options/Futures, etc.)
3. Risk Management (With Kelly Criterion) && Calculate Positional Probabilities
4. Deposit Module (Offload Portion of Profits with API's to Coinbase/Prosper/Bank Accts(Stripe))
"""

class MMU(object):
	def __init__(self, arg):
		self.arg = arg

class Universe(object):
	def __init__(self, arg):
		self.arg = arg

class Deposit(object):
	def __init__(self, arg):
		self.arg = arg
		
		