from matplotlib import pyplot as plt
import yfinance as yf

class HistoricalData:
    def __init__(self, tickers, start, end, interval):
        if type(tickers) == list:
            self.data = {}
            for ticker in tickers:
                stock = yf.Ticker(ticker)
                self.data[ticker] = stock.history(interval=interval, start=start, end=end)
        else:
            stock = yf.Ticker(tickers)
            self.data = stock.history(interval=interval, start=start, end=end)

    def get_data(self):
        return self.data

    def plot_data(self):
        if type(self.data) == dict:
            values = list(self.data.values())
            keys = list(self.data.keys())
            if len(self.data) == 1:
                _, axis = plt.subplots(1, figsize=(45, 10))
                axis.plot(values[0].index, values[0].Close, color='green')
                axis.set_title(f'Historical data for {keys[0]}')
                axis.set_xlabel('Time')
                axis.set_ylabel('Closing Price')
            else:
                plotnum = 0
                _, axes = plt.subplots(len(self.data), figsize=(45, 25))
                for _, (asset, df) in enumerate(zip(keys, values)):
                    axes[plotnum].plot(df.index, df.Close, label=f'{asset}', color='blue')
                    axes[plotnum].set_title(f'Historical data for {asset}')
                    axes[plotnum].set_xlabel('Time')
                    axes[plotnum].set_ylabel('Closing Price')
                    plotnum += 1
        else:
            _, axis = plt.subplots(1, figsize=(45, 10))
            axis.plot(self.data.index, self.data.Close, color='green') 