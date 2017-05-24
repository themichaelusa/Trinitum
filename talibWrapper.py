import talib as tb
from talib import abstract
from talib.abstract import *
import numpy as np
import pandas as pd

def generateInputDict(self, dataframe): 

    talibInputs = {
    'open': np.asarray(dataframe["open"].tolist()),
    'high': np.asarray(dataframe["high"].tolist()),
    'low': np.asarray(dataframe["low"].tolist()),
    'close': np.asarray(dataframe["close"].tolist()),
    'volume': np.asarray(dataframe["volume"].tolist())
    }

    return talibInputs

class TalibHistWrapper(object):

    def __init__(self, init, *args):
        
        self.init = init
        self.tbArgs = args

        self.inputsDict = {
        'MA': self.MOV_A(self.init, *self.tbArgs)
        'BBANDS': self.BOL_BANDS(self.init, *self.tbArgs)
        }

    def getIndicator(self, indicator):
        return self.inputsDict[indicator]
        
    def MOV_A(init, ma_type, timeperiod):

        inputs = init
        return tb.MA(inputs, timeperiod, ma_type)

    def BOL_BANDS(init, ma_type, nbdevup, nbdevdn, timeperiod):

        inputs = init
        upper, middle, lower = tb.BBANDS(inputs, timeperiod, nbdevup, nbdevdn, ma_type)
        return (upper, middle, lower)
