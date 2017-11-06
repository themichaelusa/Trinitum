import empyrical

class RiskProfile(object):

    def __init__(self, riskDict, returns=None, riskFree=None):
        self.selected = riskDict
        self.analytics = RiskAnalytics()

    def updateRiskFreeRate(self, newRate):
        if type(newRate) == float:
            self.analytics.riskFreeRate = newRate

    def updateReturns(self, newReturns):
        if type(newReturns) == float:
            self.analytics.returns = newReturns

    def getAnalytics(self):
        return [self.analytics.getAnalytic(k,v) for k,v in self.selected.values()]
        
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
        'DOWNSIDE_RISK': self.getDownsideRisk
        }

        self.returns, self.riskFreeRate = None, None

    def getAnalytic(self, key, value):
        return self.funcDict[key](*value)
    
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

    def getAnnualReturn(self, period='daily', annualization=None)
        return empyrical.annual_return(self.returns, period, annualization)

    def getCumReturns(self, starting_value=0):
        return empyrical.cum_returns(self.returns, starting_value)

    def getAnnualVolatility(self, period='daily', alpha=2.0, annualization=None):
        return empyrical.annual_volatility(self.returns, period, alpha, annualization)

    def getDownsideRisk(self, required_return=0, period='daily', annualization=None):
        return empyrical.downside_risk(self.returns, required_return, period, annualization)

    """
    def getCalmarRatio(returns, period='daily', annualization=None)
        return empyrical.calmar_ratio(returns, period, annualization)

    def getOmegaRatio(returns, risk_free=0.0, required_return=0.0, annualization=252):
        return empyrical.omega_ratio(returns, risk_free=, required_return, annualization)

    def getSortinoRatio(returns, required_return=0, period='daily', annualization=None, _downside_risk=None):
        return empyrical.sortino_ratio(returns, required_return, period,  annualization, _downside_risk)
    """