class Logger(object):

	def __init__(self, name, ext='.txt'):
		self.filename = name + ext

	def addEvent(self, eventName, eventDesc):
		from .Utilities import getCurrentTime
		event = getCurrentTime() + ' ' + eventName + '| ' + eventDesc + '\n'
		with open(self.filename, "a+") as file:
			file.write(event)
		print(event)
		
class ResultFormatter(object):
	
	def __init__(self, gemName, logName):
		self.logName = logName
		self.results = gemName + '_results'
		self.ordersCSV = gemName + '_orderbook.csv'
		self.positionsCSV = gemName + '_positionbook.csv'
		self.statsTXT = gemName + '_stats.txt'

	def getFormattedResults(self, rStats, cStats, oBook, pBook):
		self.booksToCSV(oBook, pBook)
		self.statsToTXT(cStats, rStats)
		self.generateResultsFolder()

	def generateResultsFolder(self):
		from subprocess import call
		call(['mkdir', self.results])
		call(['mv', self.statsTXT, self.results])
		call(['mv', self.ordersCSV, self.results])
		call(['mv', self.positionsCSV, self.results])
		call(['mv', (self.logName), self.results])

	def booksToCSV(self, orderBook, positionBook): 
		from pandas import DataFrame
		oBookDF = DataFrame.from_dict(orderBook)
		pBookDF = DataFrame.from_dict(positionBook)
		oBookDF.to_csv(self.ordersCSV, sep='\t')
		pBookDF.to_csv(self.positionsCSV, sep='\t')

	def statsToTXT(self, captialStats, riskStats):

		capitalStatsList = captialStats.items()
		riskStatsList = riskStats.items()

		with open(self.statsTXT, "a+") as file:
			
			file.write('CAPITAL_STATISTICS: \n')
			for c in capitalStatsList:
				stat, value = c
				if(stat == 'id'): continue
				file.write((str(stat) + ": " + str(value) + '\n'))

			file.write('RISK_STATISTICS: \n')
			for r in riskStatsList:
				stat, value = r
				if(stat == 'id'): continue
				file.write((str(stat) + ": " + str(value) + '\n'))
