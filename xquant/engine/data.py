# -*- coding: utf-8 -*-

"""
DataHandler抽象基类

@author:
@version: 0.5.2
"""

import datetime
import os
import sys
import pandas as pd
import functools
from collections import namedtuple
from abc import ABCMeta, abstractmethod
from xquant.engine.event import BarEvent
from datetime import datetime
import ccxt




class DataHandler(object):
    """
    DataHandler抽象基类，不允许直接实例化，只用于继承
    继承的DataHandler对象用于对每个symbol生成bars序列（OHLCV）
    这里不区分历史数据和实时交易数据
    """
    Bar = namedtuple('Bar', ('symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume'))

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        从latest_symbol列表中返回最近的几根bar，
        如果可用值小于N，则返回全部所能的使用k bar
        """
        raise NotImplementedError("Should implement get_latest_bars()!")

    @abstractmethod
    def update_bars(self):
        """
        将股票列表中bar(条状图，k线)更新到最近的那一根
        """
        raise NotImplementedError("Should implement update_bars()！")


######################
# 对不同数据来源具体处理 #
######################

class CSVDataHandler(DataHandler):
    def __init__(self, events, csv_dir, symbol_list, start_date, end_date):
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.start_date = start_date
        self.end_date = end_date

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        从数据文件夹中打开CSV文件，转换成pandas的DataFrames格式，union所有股票index, 数据向前填充
        列：'datetime','open','high','low','close','volume' 日期升序排列
        """
        comb_index = None
        for s in self.symbol_list:
            self.symbol_data[s] = pd.read_csv(
               self.csv_dir,
                header=0, index_col=0, parse_dates=True,
                names=['datetime', 'open', 'high', 'low', 'close', 'volume']
            ).sort_index()
            # if not isinstance(self.symbol_data[s]['datetime'],datetime.datetime) :
            # print(self.symbol_data[s])
            print('1111111111111111')
            # self.symbol_data[s]['datetime'] = pd.to_datetime(self.symbol_data[s]['datetime'])
            # print(self.symbol_data[s].head(5))
            print(self.symbol_data[s].info())

            # self.symbol_data[s]=self.symbol_data[s][self.start_date:self.end_date]
            print('1111111')
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)
            self.latest_symbol_data[s] = []

        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()

    def _get_new_bar(self, symbol):
        """
        返回最新的bar，格式为(symbol, datetime, open, high, low, close, volume)
        生成器，每次调用生成一个新的bar，直到数据最后，在update_bars()中调用
        """
        for b in self.symbol_data[symbol]:
            # print(DataHandler.Bar(symbol, b[0], b[1][0], b[1][1], b[1][2], b[1][3], b[1][4]),'111111111122222222')
            yield DataHandler.Bar(symbol, b[0], b[1][0], b[1][1], b[1][2], b[1][3], b[1][4])


    def get_latest_bars(self, symbol, N=1):
        """
        从latest_symbol列表中返回最新的N个bar，或者所能返回的最大数量的bar
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bars_list[-N:]

    def get_latest_bar(self, symbol):
        """
        从latest_symbol列表中直接返回最后的bar
        而get_latest_bars(symbol, N=1)返回元素只有最后一个bar的list
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bars_list[-1]

    def get_latest_bar_datetime(self, symbol):
        """
        返回最后一个bar的Python datetime对象
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bars_list[-1][1]

    def update_bars(self):
        """
        对于symbol list中所有股票，将最新的bar更新到latest_symbol_data字典
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))  #生成器扔出来的时候，就已经完全做好了，可以直接拿来用。
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
                    # print(BarEvent(bar),'woshishisceshi')
                    self.events.put(BarEvent(bar))
                    # 这里有了bar之后，就把这个事件推送到队列里面去。


class HDF5DataHandler(DataHandler):
    pass



class ArbitrageDate(DataHandler):
    exchangeok = ccxt.okex3()

    '''经过一上午的反思我终于知道这里改如何写了，写一个DATe生成器，同时得到两个交易所，的价格
    然后计算价差，对到队列中去，队列拿到后，根据策略去计算这个价差，整个套利流程就到一块了，获取合约
    的websockt单独弄一个api模块，封到外面去，这样还做到了解耦和复用。
    在这里的实现是用队列，api那面接到数据后处理完成把干净对数据直接对到队列里，这面从队列里拿，拿走算价差，最后推给新的队列
    时间上目前细粒度要求不高，所以1m以上都OK，不用考虑tick的问题，也就是1分钟去交易所拉或者推一次就行，毕竟不是高频套利。
    这里只是把两个合约打个包然后直接给回测，具体的处理由策略来做，在这里不要去求价差，这么做并不合理和连续。
    '''
    def __init__(self,events,symbol_list,exchange=exchangeok):
        self.exchange = exchange
        self.symbol_list = symbol_list
        self.events = events
        self.continue_backtest = True

    def _make_adate(self):
        '''具体的数据解封，交给strgerty,这里就直接打包好数据就行。不要算出价差，不需要这样
        这里只是把两个合约打个包然后直接给回测，具体的处理由策略来做，在这里不要去求价差，这么做并不合理和连续。
        '''
        b = self.exchange.fetch_ohlcv(symbol='BTC-USD-SWAP',timeframe='1m',limit=1)
        b = b[0]                      #为了和接口对接上，这里考虑是DF? 两个DF相减，理论上也是可以的啊。
        bar = DataHandler.Bar('OKex',datetime.fromtimestamp(b[0]/1000), b[1], b[2], b[3], b[4], b[5])
        print(bar,'111111111111')
        return bar

    def get_latest_bars(self, symbol, N=1):
        '''从latest_symbol列表中返回最新的N个bar，或者所能返回的最大数量的bar
        这里主要是为了计算指标的，暂时不用实现。套利不需要指标。'''
        pass

    def update_bars(self):
        bar = self._make_adate()
        if bar is not None:
            # self.latest_symbol_data[s].append(bar)

            self.events.put(BarEvent(bar))
            # 这里有了bar之后，就把这个事件推送到队列里面去。







