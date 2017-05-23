import time
import datetime
import itertools
import pandas as pd
import numpy as np
import codecs
import requests
import csv
import io
import pytz
import urllib.request
import matplotlib as mpl

PROTOCOL = 'http://'
BASE_URL = 'www.google.com/finance/getprices'

def getGoogleIntradayData(ticker, interval, lookback, end_time = time.time()):

    resource_url = PROTOCOL + BASE_URL
    payload = {
        'q': ticker,
        'i': str(interval),
        'p': str(lookback) + 'd',
        'ts': str(int(end_time * 1000)),
        'f': 'd,o,h,l,c,v'
    }

    r = requests.get(resource_url, params = payload)
    quotes = []

    with io.BytesIO(r.content) as csvfile:

        quote_reader = csv.reader(codecs.iterdecode(csvfile, 'utf-8'))
        timestamp_start = None
        timestamp_offset = None
        timezone_offset = 0

        for row in quote_reader:

            if row[0][:16] == 'TIMEZONE_OFFSET=':
                timezone_offset = -1 * int(row[0][16:])
            elif row[0][0] not in 'a1234567890':  # discard headers
                continue
            elif row[0][0] == 'a':  # 'a' prepended to the timestamp that starts each day
                timestamp_start = pytz.utc.localize(datetime.datetime.fromtimestamp(float(row[0][1:])) + datetime.timedelta(minutes=timezone_offset))
                timestamp_offset = 0
            elif timestamp_start:
                timestamp_offset = int(row[0])

            if not timestamp_start and not timestamp_offset:
                continue

            timestamp = timestamp_start + datetime.timedelta(seconds=timestamp_offset * interval)
            closing_price = float(row[1])
            high_price = float(row[2])
            low_price = float(row[3])
            open_price = float(row[4])
            volume = float(row[5])

            quotes.append((timestamp, closing_price, high_price, low_price, open_price, volume))

    df = pd.DataFrame(quotes, columns = ['datetime', 'close', 'high', 'low', 'open', 'volume'])
    datesToReturn = df['datetime']
    df = df.set_index('datetime')

    return (df, datesToReturn)


