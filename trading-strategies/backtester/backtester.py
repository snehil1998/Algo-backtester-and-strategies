import math
from matplotlib import pyplot as plt


class Backtester:
    def __init__(self, strategy, data, trade_commission, amount_invested, leverage_ratio):
        self.strategy = strategy
        self.data = data
        self.trade_commission = trade_commission
        self.amount_invested = amount_invested
        self.leverage_ratio = leverage_ratio
        self.position = 'close'
        self.data['Market Returns'] = self.data['Close'].pct_change().fillna(0)
        self.data['Cumulative Strategy Returns'] = 0
        self.data['Trade Type'] = 0
        self.profit_trades = 0
        self.loss_trades = 0
        self.buy = []
        self.sell = []
        self.close = []
        for key, value in self.strategy.positions.items():
            if value == 'buy':
                self.buy.append(key)
            elif value == 'sell':
                self.sell.append(key)
            else:
                self.close.append(key)

    def backtest(self):
        cash = self.amount_invested * self.leverage_ratio
        previous_cash = self.amount_invested * self.leverage_ratio
        for i in self.data.index:
            if (self.position == 'close'):
                if (i in self.strategy.positions.keys()):
                    previous_cash = cash
                    cash = cash * (1 - self.trade_commission)
                    self.position = self.strategy.positions[i]
            else:            
                if self.position == 'buy':
                    cash = cash * (1 + self.data.at[i, 'Market Returns'])
                else:
                    cash = cash * (1 - self.data.at[i, 'Market Returns'])
                if (i in self.strategy.positions.keys()) and (self.strategy.positions[i] == 'close'):
                    self.position = 'close'
                    cash = cash * (1 - self.trade_commission)
                    if cash < previous_cash:
                        self.loss_trades += 1
                        self.data.at[i, 'Trade Type'] = -1
                    else:
                        self.profit_trades += 1
                        self.data.at[i, 'Trade Type'] = 1
            self.data.at[i, 'Cumulative Strategy Returns'] = cash
            if ((self.amount_invested * self.leverage_ratio) - cash) >= self.amount_invested:
                print('reached margin at: ', i)
                break
                
    def plot_backtest(self):
        _, axis = plt.subplots(1, figsize=(45, 25))
        plt.plot(self.data[self.data.index.isin(self.buy)].index, self.data[self.data.index.isin(self.buy)]['Cumulative Strategy Returns'], '^', markersize=10, color='g', lw=0, label='Buy Signal')
        plt.plot(self.data[self.data.index.isin(self.sell)].index, self.data[self.data.index.isin(self.sell)]['Cumulative Strategy Returns'], 'v', markersize=10, color='g', lw=0, label='Sell Signal')
        plt.plot(self.data[self.data.index.isin(self.close)].index, self.data[self.data.index.isin(self.close)]['Cumulative Strategy Returns'], 'x', markersize=10, color='r', lw=0, label='Close Signal')
        plt.plot(self.data[self.data['Trade Type'] == -1].index, (self.data[self.data['Trade Type'] == -1]['Cumulative Strategy Returns']+10), 'o', markersize=10, color='pink', lw=0, label='Loss Trade')
        plt.plot(self.data[self.data['Trade Type'] == 1].index, (self.data[self.data['Trade Type'] == 1]['Cumulative Strategy Returns']+10), 'o', markersize=10, color='y', lw=0, label='Profit Trade')
        plt.grid()
        axis.plot(self.data.index, self.data['Cumulative Strategy Returns'], color='blue')

    def get_metrics(self):
        print('Final value: ', self.data['Cumulative Strategy Returns'][-1])
        print('P&L: ', (self.data['Cumulative Strategy Returns'][-1] - (self.leverage_ratio*self.amount_invested)))
        print('Returns %: ', 100*(self.data['Cumulative Strategy Returns'][-1] - (self.leverage_ratio*self.amount_invested))/self.amount_invested)
        print('Number of trades: ', self.loss_trades + self.profit_trades)
        print('Loss trades %: ', (100*self.loss_trades)/(self.loss_trades + self.profit_trades))
        print('Profit trades %: ', (100*self.profit_trades)/(self.loss_trades + self.profit_trades))
        periodic_returns  = self.data['Cumulative Strategy Returns'].pct_change().dropna()
        window = (self.data.index[1]  - self.data.index[0]).seconds // 60
        sharpe_ratio = (periodic_returns.mean()/periodic_returns.std()) * math.sqrt(252*((60*24)/window))
        print('Annual Sharpe ratio: ', sharpe_ratio)
        print ("Max profit %: ", (100*(self.data['Cumulative Strategy Returns'].max() - (self.leverage_ratio*self.amount_invested))/self.amount_invested))
        print ("Max loss %: ", (100*(self.data['Cumulative Strategy Returns'].min() - (self.leverage_ratio*self.amount_invested))/self.amount_invested))