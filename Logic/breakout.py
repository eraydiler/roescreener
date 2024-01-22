import os, pandas

class Breakout:
    def __init__(self):
        pass

    def is_consolidating(self, df, percentage=2):
        recent_candlesticks = df[-15:]
        
        max_close = recent_candlesticks['Close'].max()
        min_close = recent_candlesticks['Close'].min()

        threshold = 1 - (percentage / 100)
        if min_close > (max_close * threshold):
            return True        

        return False

    def is_breaking_out(self, df, percentage=2.5):
        values = df[-1:]['Close'].values
        if values.size < 1:
            return False

        last_close = values[0]

        if self.is_consolidating(df[:-1], percentage=percentage):
            recent_closes = df[-16:-1]

            if last_close > recent_closes['Close'].max():
                return True

        return False


# for filename in os.listdir('datasets/intraday'):
#     df = pandas.read_csv('datasets/intraday/{}'.format(filename))
#     breakout = Breakout()

#     if breakout.is_consolidating(df, percentage=2.5):
#         print("{} is consolidating".format(filename))

#     if breakout.is_breaking_out(df, percentage=2.5):
#         print("{} is breaking out".format(filename))