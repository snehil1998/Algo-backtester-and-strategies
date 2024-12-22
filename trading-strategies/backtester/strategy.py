from matplotlib import pyplot as plt


class Strategy:
    def __init__(self, data):
        self.position = ''
        self.positions = {}
        self.data = data
        self.stop_loss = 0
        self.take_profit = 0
        self.data['Positions'] = 0
        self.data['Signal'] = 0

    def implement(self):
        pass

    def buy_trade(self, date, stop_loss = None, take_profit = None):
        if self.position == 'sell':
            raise RuntimeError('Sell position already exists and only 1 position allowed at a time. Please close the previous position first')
        self.position = 'buy'
        self.positions[date] = 'buy'
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def sell_trade(self, date, stop_loss = None, take_profit = None):
        if self.position == 'buy':
            raise RuntimeError('Buy position already exists and only 1 position allowed at a time. Please close the previous position first')
        self.position = 'sell'
        self.positions[date] = 'sell'
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def close_trade(self, date):
        self.positions[date] = 'close'
        self.position = ''


    def plot_positions(self):
        for i in self.data.index:
            if i in self.positions.keys():
                if self.positions[i] == 'buy':
                    self.data.at[i, 'Positions'] = 1
                elif self.positions[i] == 'sell':
                    self.data.at[i, 'Positions'] = -1
        # _, axis = plt.subplots(2, figsize=(45, 25))
        _, ax1 = plt.subplots(figsize=(45, 25))
        ax2 = ax1.twinx()
        ax1.plot(self.data.index, self.data['Close'], color='blue')
        ax2.plot(self.data.index, self.data['Positions'], color='green')
        ax2.plot(self.data.index, self.data['Signal'], color='red')
        # axis[0].plot(self.data.index, self.data['Close'], color='blue')
        # axis[1].plot(self.data.index, self.data['Positions'], color='green')
        # axis[1].plot(self.data.index, self.data['Signal'], color='red')

    def plot_indicators(self):
        pass

    def print_num_of_positions(self):
        print(f'number of buys: {len(self.buy)} and number of sells: {len(self.sell)}')