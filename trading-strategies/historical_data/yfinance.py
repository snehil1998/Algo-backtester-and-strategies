from matplotlib import pyplot as plt
import yfinance as yf

class HistoricalData:
    def __init__(self, ticker, start, end, interval):
        self.stock = yf.Ticker(ticker)
        self.data = self.stock.history(interval=interval, start=start, end=end)

    def get_data(self):
        return self.data

    def plot_data(self):
        _, axis = plt.subplots(1, figsize=(45, 10))
        axis.plot(self.data.index, self.data.Close, color='green') 