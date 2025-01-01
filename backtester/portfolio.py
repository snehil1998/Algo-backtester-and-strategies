from backtester.position import Position

class Portfolio:
    def __init__(self, assets=[], asset_weights=[], initial_amount=10000, commission_fee=0.0, leverage=1.0):
        if assets is []:
            raise Exception("Portfolio has no assets allocated")
        self.assets = assets
        self.inital_amount = initial_amount
        self.commission_fee = commission_fee
        self.leverage = leverage
        self.trades = {}
        self.open_positions = {}
        self.asset_allocation = {}
        for i, asset in enumerate(self.assets):
            if len(asset_weights) == 0:
                self.asset_allocation[asset] = self.inital_amount / len(assets)
            else:
                self.asset_allocation[asset] = (asset_weights[i] * self.inital_amount) / sum(asset_weights)
        
    def open_trade(self, asset, date, trade_amount, position_type: Position, price, stop_loss, take_profit):
        if asset not in self.assets:
            raise Exception(f'{asset} was not allocated to the portfolio')
        if asset in self.open_positions.keys():
            return
        if trade_amount > self.asset_allocation[asset]:
            raise Exception(f'Trade amount: {trade_amount} exceed asset allocation: {self.asset_allocation[asset]}')
        
        # Calculate notional trade amount (leveraged)
        notional_trade_amount = trade_amount * self.leverage
        # Calculate margin and commission
        commission_fee = notional_trade_amount * self.commission_fee  # Commission based on leveraged exposure
        trade_amount_with_commission = trade_amount + commission_fee
        self.asset_allocation[asset] -= trade_amount_with_commission
        
        self.open_positions[asset] = {
            'asset': asset,
            'date': date,
            'type': position_type,
            'entry_price': price,
            "trade_amount": notional_trade_amount,
            "margin": trade_amount,
            'stop_loss': stop_loss,
            'take_profit': take_profit
        }
            
    def close_trade(self, asset, position, date, exit_price):
        if position['type'] == Position.BUY:
            profit_percentage = ((exit_price - position['entry_price']) / position['entry_price'])
        if position['type'] == Position.SELL:
            profit_percentage = ((position['entry_price'] - exit_price) / position['entry_price'])
        
        profit = position['trade_amount'] * profit_percentage
        
        # Revenue after commission
        revenue = position["margin"] + profit
        commission_fee = (position['trade_amount']+profit) * self.commission_fee
        revenue -= commission_fee 
        self.asset_allocation[asset] += revenue
        
        if asset not in self.trades:
                self.trades[asset] = []
        self.trades[asset].append(
            {
                'asset': asset,
                'entry_date': position['date'],
                'date': date,
                'type': position['type'],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'trade_amount': position['trade_amount'],
                'margin': position['margin'],
                'profit': revenue - position["margin"],
                'profit_percentage': ((revenue - position["margin"])/position['margin']) * 100
            }
        )
        self.open_positions.pop(asset)
