
def generateInputDict(self, dataframe): 

	talibInputs = {
    'open': np.asarray(dataframe["open"].tolist()),
    'high': np.asarray(dataframe["high"].tolist()),
    'low': np.asarray(dataframe["low"].tolist()),
    'close': np.asarray(dataframe["close"].tolist()),
    'volume': np.asarray(dataframe["volume"].tolist())
    }

    return talibInputs

def MOV_A(init, ma_type, timeperiod):

    inputs = init
    return MA(inputs, timeperiod, ma_type)

def BOL_BANDS(init, ma_type, nbdevup, nbdevdn, timeperiod):

    inputs = init
    upper, middle, lower = BBANDS(inputs, timeperiod, nbdevup, nbdevdn, ma_type)
    return (upper, middle, lower)
