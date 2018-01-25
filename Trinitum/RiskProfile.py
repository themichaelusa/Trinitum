import empyrical

class RiskProfile(object):

    def __init__(self, name, params):
        self.analyticsObj = RiskAnalytics()
        self.analyticsList = []
        self.parameters = params

    def updateRiskFreeRate(self, newRate):
        if type(newRate) == float:
            self.analyticsObj.riskFreeRate = newRate

    def updateReturns(self, newReturns):
        if type(newReturns) == float:
            self.analyticsObj.returns = newReturns

    def addAnalytic(self, analyticName):
        self.analyticsList.append(analyticName)

    def getAnalytics(self):
        analytics = {a:self.analyticsObj.getAnalytic(a) for a in self.analyticsList}
        return analytics
        
class RiskAnalytics(object):
    
    def __init__(self):

        self.funcDict = {
        'MAX_DRAWDOWN': self.getMaxDrawdown,
        'SHARPE_RATIO': self.getSharpeRatio,
        'ALPHA': self.getAlpha,
        'BETA': self.getBeta,
        'CAGR': self.getCAGR,
        'ANNUAL_RETURNS': self.getAnnualReturn,
        'CUMULATIVE_RETURNS': self.getCumReturns,
        'ANNUAL_VOLATILITY': self.getAnnualVolatility,
        'DOWNSIDE_RISK': self.getDownsideRisk,
        'CALMAR_RATIO': self.getCalmarRatio,
        'SORTINO_RATIO': self.getSortinoRatio,
        'OMEGA_RATIO': self.getOmegaRatio,
        'KELLY': self.getKellyCriterion
        }

        self.returns, self.riskFreeRate = None, None

    def getAnalytic(self, key):
        return float(self.funcDict[key]())

    def getKellyCriterion(self): 
        winsCount, lossesCount = 0, 0
        for r in self.returns:
            if r >= 0:
                winsCount += 1
            else:
                lossesCount += 1

        probWin = winsCount/(winsCount+lossesCount)
        probLoss = 1-probWin
        wlRatio = probWin/probLoss
        return probWin - probLoss/wlRatio
    
    def getMaxDrawdown(self):
        return empyrical.max_drawdown(self.returns)

    def getSharpeRatio(self, period='daily', annualization=None):
        return empyrical.sharpe_ratio(self.returns, self.riskFreeRate, period, annualization)

    def getAlpha(self, period='daily', annualization=None):
        return empyrical.alpha(self.returns, self.riskFreeRate, period, annualization, beta_=None)

    def getBeta(self):
        return empyrical.beta(self.returns, self.riskFreeRate)

    def getCAGR(self, period='daily', annualization=None):
        return empyrical.cagr(self.returns, period, annualization)

    def getAnnualReturn(self, period='daily', annualization=None):
        return empyrical.annual_return(self.returns, period, annualization)

    def getCumReturns(self, starting_value=0):
        return empyrical.cum_returns(self.returns, starting_value)

    def getAnnualVolatility(self, period='daily', alpha=2.0, annualization=None):
        return empyrical.annual_volatility(self.returns, period, alpha, annualization)

    def getDownsideRisk(self, required_return=0, period='daily', annualization=None):
        return empyrical.downside_risk(self.returns, required_return, period, annualization)

    def getCalmarRatio(returns, period='daily', annualization=None):
        return empyrical.calmar_ratio(returns, period, annualization)

    def getOmegaRatio(returns, risk_free=0.0, required_return=0.0, annualization=252):
        return empyrical.omega_ratio(returns, risk_free, required_return, annualization)

    def getSortinoRatio(returns, required_return=0, period='daily', annualization=None, _downside_risk=None):
        return empyrical.sortino_ratio(returns, required_return, period,  annualization, _downside_risk)
