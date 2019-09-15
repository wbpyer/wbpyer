# import datetime
# import pandas as pd
# start_date = datetime.datetime(2017, 7, 1,0,0)
# print(type(start_date))
# print(str(start_date))
#
# df = pd.read_csv('D:\coin_quant_ class_0518\coin_quant_class\data\eos1m.csv')
# print(type(df['candle_begin_time']))
# df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'])
#
# print(df.info())

# import asyncio
#
# async def main():
#     while True:
#         print('Hello ...')
#         # await asyncio.sleep(1)
#         print('... World!')
#         await asyncio.sleep(1)
#
# # Python 3.7+
# asyncio.run(main())
# from xquant.engine.okex_api import dataqueue
# # from xquant.engine.data import ArbitrageDate
# # ArbitrageDate(dataqueue=dataqueue)._make_adate()
# # print('go')
#
# print(dataqueue.get(timeout=2))
#今天先写到这里，明天继续，目前写到了如何让TEST和api 利用队列通信，能够拿到实时的数据并做各种处理。
# import time
# from xquant.engine.okex_api import dataqueue
# for i in range(3):
#     time.sleep(2)
#     print(dataqueue.get(i))
'''今天先写到这里，目前准备去健身，明天继续写，目前写到数据之间的通信有点问题，就是怎么把API的数据，给到HANDLER,
怎么去通信的问题。，明天上午继续。。'''
from xquant.engine.data import ArbitrageDate,BarEvent
import ccxt
aa = ArbitrageDate(BarEvent,exchange=ccxt.okex3())
aa._make_adate()


'''测试成功，顺利拿到我想要的数据。'''