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

    def __init__(self, ticker, assetType, start, end, interval, unit):
        if assetType == 'Stock':
            self.get_stock_data(ticker, start, end, interval, unit)
        else:
            self.get_crypto_data(ticker, start, end, interval, unit)
        

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
        self.data = data.reset_index(['symbol']).drop(['symbol'], axis=1)
    
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
        self.data = data.reset_index(['symbol']).drop(['symbol'], axis=1)
        self.data = self.data.reset_index().drop_duplicates(subset='timestamp', keep='last').set_index('timestamp')

    def get_data(self):
        return self.data

    def plot_data(self):
        _, axis = plt.subplots(1, figsize=(45, 10))
        axis.plot(self.data.index, self.data.Close, color='green') 