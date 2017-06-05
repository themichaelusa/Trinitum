import talib as tb
from talib import abstract
from talib.abstract import *
import numpy as np
import pandas as pd
import Utilities as utl

def generateInputDict(dataframe): 

    talibInputs = {
    'open': np.asarray(dataframe["open"].tolist(), dtype ='f8'),
    'high': np.asarray(dataframe["high"].tolist(), dtype ='f8'),
    'low': np.asarray(dataframe["low"].tolist(), dtype ='f8'),
    'close': np.asarray(dataframe["close"].tolist(), dtype ='f8'),
    'volume': np.asarray(dataframe["volume"].tolist(), dtype ='f8')
    }

    return talibInputs

class TalibHistWrapper(object):

    def __init__(self, init, args):
        
        self.inputs = init
        self.tbArgs = args

    def getIndicator(self, indicator):

        try:

            inputsDict = {
            'MA': MA, # tbArgs:  ma_type, timeperiod
            'BBANDS': BBANDS, #tbArgs: timeperiod, nbdevup, nbdevdn, ma_type
            'AROON': AROON,
            }    

            outputs = inputsDict[indicator](self.inputs, *self.tbArgs)
            listOutputs = [a.tolist() for a in outputs]
            if (len([listOutputs]) == 1): return [listOutputs]
            else: return listOutputs

        except ValueError: pass
    
    """
    # ---------------- MOMENTUM INDICATORS ----------------------
    def TB_MACD(self):

        fastperiod, slowperiod, signalperiod, *_ = self.tbArgs
        macdreg = abstract.MACD
        macd, macdsignal, macdhist = MACD(self.inputs, fastperiod, slowperiod, signalperiod)
        return (ut.firstNotNAN(macd), ut.firstNotNAN(macdsignal), ut.firstNotNAN(macdhist))

    def TB_RSI(self):

        timeperiod, *_ = self.tbArgs
        rsi = abstract.RSI
        real = RSI(self.inputs, timeperiod)
        return ut.firstNotNAN(real)

    def TB_ADX(self):

        timeperiod, *_ = self.tbArgs        
        adx = abstract.ADX
        real = ADX(self.inputs, timeperiod)
        return ut.firstNotNAN(real)

    def TB_CCI(self):

        timeperiod, *_ = self.tbArgs        
        cci = abstract.CCI
        real = CCI(self.inputs, timeperiod)
        return ut.firstNotNAN(real)

    def TB_CMO(self):

        timeperiod, *_ = self.tbArgs        
        cmo = abstract.CMO
        real = CMO(self.inputs, timeperiod)
        return ut.firstNotNAN(real)

    def TB_AROON(self):

        timeperiod, *_ = self.tbArgs        
        aroon = abstract.AROON
        aroondown, aroonup = AROON(self.inputs, timeperiod)
        return (ut.firstNotNAN(aroondown),ut.firstNotNAN(aroonup))

    def TB_STOCH(self):

        fastk_period, slowk_period, lowk_matype, lowk_matype, slowd_matype, *_ = self.tbArgs        
        stoch = abstract.STOCH
        slowk, slowd = STOCH(self.inputs, fastk_period, slowk_period, slowk_matype, lowk_matype, slowd_matype)
        return (ut.firstNotNAN(slowk), ut.firstNotNAN(slowd))

    def TB_STOCHF(self):

        fastk_period, fastd_period, fastd_matype, *_ = self.tbArgs        
        stochf = abstract.STOCHF
        fastk, fastd = STOCHF(self.inputs, fastk_period, fastd_period, fastd_matype)
        return (ut.firstNotNAN(fastk), ut.firstNotNAN(fastd))

    def TB_ULTOSC(self):

        timeperiod1, timeperiod2, timeperiod3, *_ = self.tbArgs        
        ultosc = abstract.ULTOSC
        real = ULTOSC(self.inputs, timeperiod1, timeperiod2, timeperiod3)
        return ut.firstNotNAN(real)

    def TB_WILLR(self):

        timeperiod, *_ = self.tbArgs        
        willr = abstract.WILLR
        real = AROON(self.inputs, timeperiod)
        return ut.firstNotNAN(real)

    # ---------------- VOLATILITY INDICATORS ----------------------
    def TB_ATR(self):

        timeperiod, *_ = self.tbArgs        
        atr = abstract.ATR
        real = ATR(self.inputs, timeperiod)
        return ut.firstNotNAN(real)

    def TB_NATR(self):

        timeperiod, *_ = self.tbArgs        
        natr = abstract.NATR
        real  = NATR(self.inputs, timeperiod)
        return ut.firstNotNAN(real)

    def TB_TRANGE(self):

        trange = abstract.TRANGE
        real = TRANGE(self.inputs)
        return ut.firstNotNAN(real)
    """
