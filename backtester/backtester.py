from matplotlib import pyplot as plt
import pandas as pd
from backtester.position import Position
from backtester.strategy import Strategy
from backtester.portfolio import Portfolio 
import talib as ta

class Backtester:
    def __init__(self, portfolio: Portfolio, data, strategy: Strategy, stop_loss_multiplier=None, take_profit_multiplier=None, atr_period=14):
        self.portfolio = portfolio
        self.data = data
        self.strategy = strategy
        self.stop_loss_multiplier = stop_loss_multiplier
        self.take_profit_multiplier = take_profit_multiplier
        self.atr_period = atr_period
        self.signal = 0
        index = list(self.data.values())[0].index
        self.portfolio_cumulative_strategy_returns = pd.Series(0, index)
        self.portfolio_cumulative_market_returns = pd.Series(0, index)
    
    def run(self):
        for asset, df in self.data.items():
            self.strategy.initialize_indicators(df)
            df['Position'] = self.strategy.generate_positions(df)
            df['ATR'] = ta.ATR(df.High, df.Low, df.Close, self.atr_period)
            df['Signal'] = 0
            self.signal = 0
            cash = self.portfolio.asset_allocation[asset]
            exposure = 0
            df['Market_Returns'] = df['Close'].pct_change()
            df['Cumulative_Market_Returns'] = self.portfolio.asset_allocation[asset] * (1 + df['Market_Returns']).cumprod()
            df['Cumulative_Strategy_Returns'] = 0.0
            for i in range(len(df)):
                row = df.iloc[i]
                date = df.index[i]
                    
                if row['Position'] in [Position.BUY, Position.SELL]:
                    exposure = cash * self.portfolio.leverage
                    cash -= (exposure * self.portfolio.commission_fee)
                
                if self.signal == 1:
                    t = exposure
                    exposure *= (1 + df.loc[date, 'Market_Returns'])
                    cash += (exposure - t)
                elif self.signal == -1:
                    t = exposure
                    exposure *= (1 - df.loc[date, "Market_Returns"])
                    cash += (exposure - t)
                
                
                if self._manage_open_positions(asset, row, date):
                    cash *= (1 - self.portfolio.commission_fee)
                    exposure = 0
                    self.signal = 0
                
                df.loc[date, "Cumulative_Strategy_Returns"] = cash
                
                if cash <= 0:
                    print(f'Reached margin call for {asset} on {date}')
                    break
                
                position = row['Position']
                if position and position == Position.BUY:
                    self._execute_trade(asset, date, Position.BUY, row["Close"], row['ATR'])
                    self.signal = 1
                elif position and position == Position.SELL:
                    self._execute_trade(asset, date, Position.SELL, row["Close"], row['ATR'])
                    self.signal = -1  
                                  
                df.loc[date, "Signal"] = self.signal
            
            if asset in self.portfolio.open_positions.keys():
                position = self.portfolio.open_positions[asset]
                self.portfolio.close_trade(asset, position, date, row['Close']) 
                df.loc[date, "Signal"] = 0
                           
            self.portfolio_cumulative_market_returns += df['Cumulative_Market_Returns']
            self.portfolio_cumulative_strategy_returns += df['Cumulative_Strategy_Returns']

                    
    def _execute_trade(self, asset, date, position_type, price, ATR):
        trade_amount = self.portfolio.asset_allocation[asset]
        stop_loss = None
        take_profit = None
        if self.stop_loss_multiplier != None:
            stop_loss = price - self.stop_loss_multiplier*ATR if position_type == Position.BUY else price + self.stop_loss_multiplier*ATR
        if self.take_profit_multiplier != None:
            take_profit = price + self.take_profit_multiplier*ATR if position_type == Position.BUY else price - self.take_profit_multiplier*ATR
        self.portfolio.open_trade(asset, date, trade_amount, position_type, price, stop_loss, take_profit)
    
    def _manage_open_positions(self, asset, row, date):
        if asset in self.portfolio.open_positions.keys():
            position = self.portfolio.open_positions[asset] 
                    
            if position['take_profit'] != None:
                if (position['type'] == Position.BUY and row['Close'] >= position['take_profit']):
                    self.portfolio.close_trade(asset, position, date, row['Close'])   
                    return True
                elif (position['type'] == Position.SELL and row['Close'] <= position['take_profit']):
                    self.portfolio.close_trade(asset, position, date, row['Close'])
                    return True
            else:
                if (position['type'] == Position.BUY and row['Position'] in [Position.CLOSE, Position.SELL]):
                    self.portfolio.close_trade(asset, position, date, row['Close'])
                    return True
                elif (position['type'] == Position.SELL and row['Position'] in [Position.CLOSE, Position.BUY]): 
                    self.portfolio.close_trade(asset, position, date, row['Close'])
                    return True
            
            if position['stop_loss'] != None: 
                if (position['type'] == Position.BUY and row['Close'] <= position['stop_loss']):
                    self.portfolio.close_trade(asset, position, date, row['Close'])  
                    return True
                elif (position['type'] == Position.SELL and row['Close'] >= position['stop_loss']):
                    self.portfolio.close_trade(asset, position, date, row['Close'])
                    return True
        return False
        
    def plot_signals(self):
        _, ax1 = plt.subplots(len(self.portfolio.assets), figsize=(45, len(self.portfolio.assets)*10))
        if len(self.portfolio.assets) == 1:
            df = self.data[self.portfolio.assets[0]]
            ax2 = ax1.twinx()
            ax1.plot(df.index, df['Close'], color='blue')
            ax2.plot(df.index, df['Signal'], color='red')
            ax1.set_title(f"Signals for {self.portfolio.assets[0]}")
        else:
            for i, asset in enumerate(self.portfolio.assets):
                df = self.data[asset]
                ax2 = ax1[i].twinx()
                ax1[i].plot(df.index, df['Close'], color='blue')
                ax2.plot(df.index, df['Signal'], color='red')
                ax1[i].set_title(f"Signals for {asset}")
    
    def plot_returns_for_assets(self):
        _, ax1 = plt.subplots(len(self.portfolio.assets), figsize=(45, len(self.portfolio.assets)*10))
        for i, asset in enumerate(self.portfolio.assets):
            df = self.data[asset]
            buy_signals = []
            sell_signals = []
            profit_trades = []
            loss_trades = []
            
            for trade in self.portfolio.trades[asset]:
                buy_signals.append(trade['entry_date'])
                sell_signals.append(trade['date'])
                if trade['profit'] >= 0:
                    profit_trades.append(trade['date'])
                else:
                    loss_trades.append(trade['date'])
            
            if len(self.portfolio.assets) == 1:
                ax1.plot(df.index, df['Cumulative_Market_Returns'], color='blue')
                ax1.plot(df.index, df['Cumulative_Strategy_Returns'], color='black')
                ax1.plot(loss_trades, (df.loc[loss_trades,'Cumulative_Strategy_Returns']+400), 'o', markersize=20, color='pink', lw=0, label='Loss Trade')
                ax1.plot(profit_trades, (df.loc[profit_trades,'Cumulative_Strategy_Returns']+400), 'o', markersize=20, color='y', lw=0, label='Profit Trade')
                ax1.plot(buy_signals, df.loc[buy_signals,'Cumulative_Strategy_Returns'], '^', markersize=20, color='g', lw=0, label='Buy Signal')
                ax1.plot(sell_signals, df.loc[sell_signals,'Cumulative_Strategy_Returns'], 'v', markersize=20, color='r', lw=0, label='Sell Signal')
            else:        
                ax1[i].plot(df.index, df['Cumulative_Market_Returns'], color='blue')
                ax1[i].plot(df.index, df['Cumulative_Strategy_Returns'], color='black')
                ax1[i].plot(loss_trades, (df.loc[loss_trades,'Cumulative_Strategy_Returns']+50), 'o', markersize=20, color='pink', lw=0, label='Loss Trade')
                ax1[i].plot(profit_trades, (df.loc[profit_trades,'Cumulative_Strategy_Returns']+50), 'o', markersize=20, color='y', lw=0, label='Profit Trade')
                ax1[i].plot(buy_signals, df.loc[buy_signals,'Cumulative_Strategy_Returns'], '^', markersize=20, color='g', lw=0, label='Buy Signal')
                ax1[i].plot(sell_signals, df.loc[sell_signals,'Cumulative_Strategy_Returns'], 'v', markersize=20, color='r', lw=0, label='Sell Signal')
    
    
    def plot_portfolio_returns(self):
        _, ax1 = plt.subplots(figsize=(45, 10))
        ax1.plot(self.portfolio_cumulative_market_returns.index, self.portfolio_cumulative_market_returns, color='blue')
        ax1.plot(self.portfolio_cumulative_strategy_returns.index, self.portfolio_cumulative_strategy_returns, color='black')
        ax1.set_title(f"Portfolio returns")
