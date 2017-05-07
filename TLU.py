import math

"""
Trading Logic Unit:

Inputs:
1. Data (any datastream or pipeline you want. Up to the user.)
2. Blocks (references to Functions that input data and return T/F)
3. Rules (rules for buying/selling/holding)
4. Functions (custom/default cost functions for voter module)
5. MMU Feed (Universe, Currently Trading, Current Capital, Kelly Criterion, Commission, Deposit Stream, etc...)

Flow:
1. Data (for current Tick) is passed into Blocks and outputs are generated. Ex. 5 Functions --> TTFTF
2. Rules applied to combined data output. Ex. 001: BUY, 110: SELL, 101: HOLD
3. Functions (optional) applied to to combined data output. (Thresholds, Counts, Cost Funcs...)
4. Rules ---> -1/0/1 (SELL/HOLD/BUY) * Functions (some discrete non-zero value)
5. (Rules * Functions value) + MMU Feed ----> Voter Module ----> Output

Output: (-1/0/1) ----> (SELL/HOLD/BUY)
"""

class TLU(object):

	def __init__(self, data, blocks, rules, funcs = None):

		self.data = data
		self.blocks = blocks
		self.rules = rules
		self.funcs = funcs

		self.MMU_DATA = True # temporary until MMU Module is built
		# self.MMU_DATA = mmu.getTickUpdate() (what it'll look like once MMU.py is done)
		self.parsedLogic = self.parseLogicBlocks()
		self.rulesVerdict = self.applyRules()
		self.functionsVerdict = self.applyFunctions()

		self.voterInstance = self.Voter(self.rulesVerdict, self.functionsVerdict, self.MMU_DATA)
		self.voterVerdict = self.voterInstance.posDecision
		# du.pushData(self.parsedLogic, self.rulesVerdict, self.voterVerdict) (once DU.y is done)

	def mount(self, varType, newVar):

		if (varType == 'DATA'): self.data = newVar
		if (varType == 'LOGIC'): self.blocks = newVar
		if (varType == 'RULES'): self.rules = newVar
		if (varType == 'FUNC'): self.funcs = newVar

	def set(self, opType, *args): #add more if statements as time goes on (for modularity)
		
		if (opType == "thres"):
			self.voterInstance.setThreshold(*args)

	def parseLogicBlocks(self):

		entryLogic = ''

		for i in range(len(self.blocks)):
			entryLogic += str(self.blocks[i](self.data))

		return ((''.join(entryLogic)))

	def applyRules(self): 

		if (self.parsedLogic in self.rules[0]):
			return 1

		elif (self.parsedLogic in self.rules[1]):
			return 0

		elif (self.parsedLogic in self.rules[2]):
			return -1

	def applyFunctions(self):

		if (self.funcs == None):
			return 1;

		funcOutputs = [(self.funcs[i](self.data)) for i in self.funcs]
		return math.abs(sum(funcOutputs))

	class Voter(object):

		def __init__(self, rules, functions, mmuData):
			
			self.rfVerdict = rules*functions
			self.mmuData = mmuData
			self.posDecision = self.vote()

		def setThreshold(thresholdType, newThreshold): 

			if (thresholdType == 'BUY'):
				self.buyThreshold = newThreshold
			elif (thresholdType == 'SELL'):
				self.sellThreshold = newThreshold

		def vote(self):

			MMU_ALLCLEAR = self.mmuData
			if (not MMU_ALLCLEAR): 
				return 0

			elif (self.rfVerdict >= 1 and MMU_ALLCLEAR):
				return 1

			elif (self.rfVerdict == 0 and MMU_ALLCLEAR):
				return 0

			elif (self.rfVerdict <= -1 and MMU_ALLCLEAR):
				return -1

		def __str__(self):
			return str(self.posDecision)

	def __str__(self):
		return str(self.voterVerdict)
		