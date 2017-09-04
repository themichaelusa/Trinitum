import numpy as np

#As of now, the data parameter is an array of the end of day balances of the account
#Kelly Criterion has a different interpretation as of now, since we're only trading one equity

class RSU(object):

    def __init__(self, data):
        self.data = data

    def getSharpeRatio(self):
        
        returns = []
        for i in range(1,len(self.data)):
            returns[i-1] = (self.data[i]-self.data[i-1])/self.data[i-1]

        excess = 0
        for items in returns:
            excess = (items - CONST.DAILY_RISK_FREE_RATE) + excess

        avg_excess = excess / len(returns)
        std_return = np.std(returns)

        return (avg_excess/std_return)*np.sqrt(252)

    def getKellyCriterion(self):
        
        wins = 0
        losses = 0
        avg_gain = 0
        avg_loss = 0

        for i in range(1,len(self.data)):

            if(self.data[i] > self.data[i-1]):
                wins += 1
                avg_gain += self.data[i] - self.data[i-1]
            else:
                losses += 1
                avg_loss += self.data[i] - self.data[i-1]

        avg_gain = avg_gain / len(self.data)
        avg_loss = avg_loss / len(self.data)

        win_prob = wins / (wins + losses)
        win_loss_ratio = avg_gain/avg_loss

        return win_prob - ((1-win_prob)/win_loss_ratio)

    def getMaxDrawdown(self):
        
        maximum = max(self.data)
        minimum = min(self.data)

        return (maximum - minimum) / maximum

    def getAllStats(self):
    	dict = {'Sharpe' : getSharpeRatio(), 'KellyCriterion' : getKellyCriterion, 'maxDrawdown' : getMaxDrawdown()}
    	return dict

