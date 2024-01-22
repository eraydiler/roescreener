# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route('/')
# def index():
#   return render_template('index.html')

# if __name__ == '__main__':
#   app.run(port=5000)

import os, csv
# import talib
import yfinance as yf
import pandas
import snapshots
from flask import Flask, request, render_template
from Logic.breakout import Breakout as breakout
from Lists.patterns import patternList
from Lists.indicators import indicatorList
from Lists.timeframes import timeframeList

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    stocks = {}
    selectedTimeframe = request.form.get('timeframe')
    selectedPattern  = request.form.get('pattern')
    selectedIndicator  = request.form.get('indicator')
        
    print('timeframe: {},'.format(selectedTimeframe))
    print('pattern: {},'.format(selectedPattern))
    print('indicator: {},'.format(selectedIndicator))

    with open('datasets/symbols.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'company': row[1]}

    if request.form.get('data_reload') == 'Reload Data' and selectedTimeframe:
        snapshots.reloadData(request.form.get('timeframe'))
    # if request.form.get('pattern_scan') == 'Pattern Scan' and selectedPattern:
        # stocks = _scanForPatternWith(stocks, selectedPattern, selectedTimeframe)
    elif  request.form.get('indicator_scan') == 'Indicator Scan' and selectedIndicator:
        if selectedIndicator == "TTMSQUEEZE":
            stocks = _scanForTTMSqueezeIndicatorWith(stocks, selectedIndicator, selectedTimeframe)
        elif selectedIndicator == "BREAKOUT":
            stocks = _scanForBreakoutIndicatorWith(stocks, selectedIndicator, selectedTimeframe)
    
    return render_template(
        'index.html', 
        stocks=stocks,
        patterns=patternList, 
        pattern=selectedPattern,
        indicators=indicatorList,
        indicator=selectedIndicator,
        timeframes=timeframeList,
        timeframe=selectedTimeframe
    )

# def _scanForPatternWith(stocks, selectedPattern, selectedTimeframe):
    for filename in os.listdir('datasets/{}'.format(selectedTimeframe)):
        df = pandas.read_csv('datasets/{}/{}'.format(selectedTimeframe, filename))
        pattern_function = getattr(talib, selectedPattern)
        symbol = filename.split('.')[0]

        try:
            results = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
            last = results.tail(1).values[0]

            if last > 0:
                stocks[symbol][selectedPattern] = 'bullish'
            elif last < 0:
                stocks[symbol][selectedPattern] = 'bearish'
            else:
                stocks[symbol][selectedPattern] = None
            
        except Exception as e:
            print('failed on filename: ', filename)

    return stocks

def _scanForTTMSqueezeIndicatorWith(stocks, selectedIndicator, selectedTimeframe):
    for filename in os.listdir('datasets/{}'.format(selectedTimeframe)):
        df = pandas.read_csv('datasets/{}/{}'.format(selectedTimeframe, filename))
        symbol = filename.split(".")[0]
        if df.empty:
            continue

        df['20sma'] = df['Close'].rolling(window=20).mean()
        df['stddev'] = df['Close'].rolling(window=20).std()
        df['lower_band'] = df['20sma'] - (2 * df['stddev'])
        df['upper_band'] = df['20sma'] + (2 * df['stddev'])

        df['TR'] = abs(df['High'] - df['Low'])
        df['ATR'] = df['TR'].rolling(window=20).mean()

        df['lower_keltner'] = df['20sma'] - (df['ATR'] * 1.5)
        df['upper_keltner'] = df['20sma'] + (df['ATR'] * 1.5)

        def in_squeeze(df):
            return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

        df['squeeze_on'] = df.apply(in_squeeze, axis=1)

        if df.iloc[-4]['squeeze_on'] and df.iloc[-3]['squeeze_on'] and df.iloc[-2]['squeeze_on'] and not df.iloc[-1]['squeeze_on']:
            print("{} is coming out the squeeze".format(symbol))

            if df.iloc[-1]['Close'] > df.iloc[-1]['20sma']:
                stocks[symbol][selectedIndicator] = 'bullish'
            elif df.iloc[-1]['Close'] < df.iloc[-1]['20sma']:
                stocks[symbol][selectedIndicator] = 'bearish'
            else:
                stocks[symbol][selectedIndicator] = None

    return stocks

def _scanForBreakoutIndicatorWith(stocks, selectedIndicator, selectedTimeframe):
    for filename in os.listdir('datasets/{}'.format(selectedTimeframe)):
        df = pandas.read_csv('datasets/{}/{}'.format(selectedTimeframe, filename))
        symbol = filename.split(".")[0]
        if df.empty:
            continue
        
        if breakout().is_consolidating(df, percentage=2.5):
            print("{} is consolidating".format(filename))
            stocks[symbol][selectedIndicator] = 'consolidating'

        if breakout().is_breaking_out(df, percentage=2.5):
            print("{} is breaking out".format(filename))
            stocks[symbol][selectedIndicator] = 'breakingout'

    
    return stocks

if __name__ == '__main__':
    app.run(port=5000)