import os
import yfinance as yf
from datetime import date

def reloadData(timeframe):
    with open('datasets/symbols.csv') as f:
        for line in f:
            if "," not in line:
                continue
            symbol = line.split(",")[0]

            # download daily data
            if timeframe == 'daily':
                dailyData = yf.download(symbol, period="1y")
                dailyData.to_csv('datasets/daily/{}.csv'.format(symbol))
            # download intraday data
            elif timeframe == 'intraday':
                intradayData = yf.download(symbol, period="60d", interval="15m")
                intradayData.to_csv('datasets/intraday/{}.csv'.format(symbol))
            else:
                abort(404, description="Timeframe not found")