from matplotlib import pyplot as plt
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

class AlpacaHistoricalData:
    paper_api_key = 'PKHW6Z8TUF1VVA39U26G'
    paper_api_secret = 'tKsOZxbzGTvTCgYZxPjf7nYpeJ09lbFzSX8InA4T'
    paper_endpoint = 'https://paper-api.alpaca.markets/v2'

    live_api_key = 'AKWS3QANE3F9QUM7UD0H'
    live_api_secret = 'ZMtjbWs0RzEQjvCof4AQdxNRmZP6CHcZH21uLj8v'
    live_endpoint = 'https://api.alpaca.markets'

    stock_client = StockHistoricalDataClient(api_key=paper_api_key, secret_key=paper_api_secret)
    crypto_client = CryptoHistoricalDataClient(api_key=paper_api_key, secret_key=paper_api_secret)

    def __init__(self, tickers, assetType, start, end, interval, unit):
        if assetType == 'Stock':
            if type(tickers) == list:
                self.data = {}
                for ticker in tickers:
                    self.data[ticker] = self.get_stock_data(ticker, start, end, interval, unit)
            else:
                self.data = self.get_stock_data(tickers, start, end, interval, unit)
        else:
            if type(tickers) == list:
                self.data = {}
                for ticker in tickers:
                    self.data[ticker] = self.get_crypto_data(ticker, start, end, interval, unit)
            else:
                self.data = self.get_crypto_data(tickers, start, end, interval, unit)
        

    def get_stock_data(self, ticker, start, end, interval, unit):
        request_params = StockBarsRequest(
            symbol_or_symbols=[ticker],
            timeframe= TimeFrame(interval, unit),
            start=start,
            end=end
        )

        bars = self.stock_client.get_stock_bars(request_params)
        data = bars.df
        data.rename(columns = {'close':'Close', 'high':'High', 'low':'Low', 'open':'Open'}, inplace = True)
        data = data.reset_index(['symbol']).drop(['symbol'], axis=1)
        return data
    
    def get_crypto_data(self, ticker, start, end, interval, unit):
        request_params = CryptoBarsRequest(
            symbol_or_symbols=[ticker],
            timeframe= TimeFrame(interval, unit),
            start=start,
            end=end
        )

        bars = self.crypto_client.get_crypto_bars(request_params)
        data = bars.df
        data.rename(columns = {'close':'Close', 'high':'High', 'low':'Low', 'open':'Open'}, inplace = True)
        data = data.reset_index(['symbol']).drop(['symbol'], axis=1)
        data = data.reset_index().drop_duplicates(subset='timestamp', keep='last').set_index('timestamp')
        return data

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