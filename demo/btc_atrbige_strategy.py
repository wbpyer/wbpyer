import datetime
import pandas as pd
import numpy as np
from xquant import SignalEvent, Strategy, CSVDataHandler, SimulatedExecutionHandler, BasicPortfolio, Backtest
class BtcAtrbigeStrategy(Strategy):
    def __init__(self, bars, events, mean=0,std=0):
        """
        套利合约要自己做，现在你只有一个data就是a3,玩的就是a3就行。
        参数：
        bars: DataHandler对象
        events: Event队列对象
        mean: 长期均线的长度
        std: 短期均线的长度
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.mean = mean
        self.std = std

        self.bought = self._calculate_initial_bought()  # 或 {s: False for s in self.symbol_list}

    def _calculate_initial_bought(self):
        """
        添加symbol的持有情况到字典，初始化为未持有
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = False  # 或者'EXIT'
        return bought


    def calculate_signals(self, event):
        """
        当短期均线（如5日线）上穿长期均线（如10日线），买入；反之，卖出
        """
        if event.type == 'BAR':
            for s in self.symbol_list:
                bar = self.bars.get_latest_bar(s)
                if bar is None or bar == []:
                    continue

                bars = self.bars.get_latest_bars(s, N=20)
                if bars:
                    df = pd.DataFrame(bars, columns=['symbol','datetime','open','high','low','close','volume'])
                    self.mean = np.mean(df['close'])
                    self.std =np.std(df['close'])
                    if df['close'] < self.mean and df['close'] == self.std:

                        signal = SignalEvent(bar.symbol, bar.datetime, 'LONG')
                        self.events.put(signal)

                    elif df['close'] > self.mean and df['close'] == self.std:

                        signal = SignalEvent(bar.symbol, bar.datetime, 'SHORT')
                        #这里要产生信号事件，推送到队列里面去。
                        self.events.put(signal)



'''目前策略对接的是回测模块，0.1版本，未完成，待续'''