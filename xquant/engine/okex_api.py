'''这个模块的功能先确定一下，连接到交易所之后
1，通过websocket拿到数据，推给handler
2，完成portfolio发出来的订单的具体下单执行。
3,拿到数据后还有做成df，然后推送到套利的队列里面'''

import pandas as pd
import asyncio
import websockets
import json
import requests
import dateutil.parser as dp
import hmac
import base64
import zlib
from functools import partial


def inflate(data):
    decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
    )
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated

async def send_msg(websocket):
    while True:

        sub_param = {"op": "subscribe", "args": channels}
        sub_str = json.dumps(sub_param)
        await  websocket.send(sub_str)
        # print(f"send: {sub_str}")

        print("receive:")
        res = await websocket.recv()
        res = inflate(res)
        print(f"{res}")

        res = await websocket.recv()
        res = inflate(res).decode()
        b = res[76:-4].split(',')
        return b

async def subscribe_without_login(url, channels):
    async with websockets.connect(url) as websocket:
        await send_msg(websocket)



url = 'wss://real.okex.com:10442/ws/v3'
# asyncio.get_event_loop().run_until_complete(login(url, api_key, passphrase, seceret_key))
channels = ["swap/candle60s:BTC-USD-SWAP"]
# asyncio.get_event_loop().run_until_complete(subscribe(url, api_key, passphrase, seceret_key, channels))
# asyncio.get_event_loop().run_until_complete(unsubscribe(url, api_key, passphrase, seceret_key, channels))
asyncio.get_event_loop().run_until_complete(subscribe_without_login(url, channels))
# asyncio.get_event_loop().run_until_complete(unsubscribe_without_login(url, channels))



'''上面是ayscoio的websocket连接方式，可以循环起来，不断的拿到数据，但是封装程度还是不够，不太好用，因为没有办法和data,
耦合起来，但是我会写这种获取数据的方式，但是为了节省时间，就不去写耦合了，接下来直接用CCXT或者websocket类来实现。'''


'''下面是参考API写法。'''
# import ssl
# import hashlib
# import json
# import traceback
# import zlib
# from threading import Thread
# from time import sleep
#
# import websocket
# class OkexApi(object):
#     """交易接口"""
#
#     # ----------------------------------------------------------------------
#     def __init__(self):
#         """Constructor"""
#         self.host = 'wss://real.okex.com:10442/ws/v3'  # 服务器
#         self.apiKey = ''  # 用户名
#         self.secretKey = ''  # 密码
#
#         self.active = False  # 工作状态
#         self.ws = None  # websocket应用对象
#         self.wsThread = None  # websocket工作线程
#
#         self.heartbeatCount = 0  # 心跳计数
#         self.heartbeatThread = None  # 心跳线程
#         self.heartbeatReceived = True  # 心跳是否收到
#
#         self.reconnecting = False  # 重新连接中
#
#     # ----------------------------------------------------------------------
#     def heartbeat(self):
#         """"""
#         while self.active:
#             self.heartbeatCount += 1
#
#             if self.heartbeatCount < 10:
#                 sleep(1)
#             else:
#                 self.heartbeatCount = 0
#
#                 if not self.heartbeatReceived:
#                     self.reconnect()
#                 else:
#                     self.heartbeatReceived = False
#                     d = {'event': 'ping'}
#                     j = json.dumps(d)
#
#                     try:
#                         self.ws.send(j)
#                     except:
#                         msg = traceback.format_exc()
#                         self.onError(msg)
#                         self.reconnect()
#
#     # ----------------------------------------------------------------------
#     def reconnect(self):
#         """重新连接"""
#         if not self.reconnecting:
#             self.reconnecting = True
#
#             self.closeWebsocket()  # 首先关闭之前的连接
#             self.heartbeatReceived = True  # 将心跳状态设为正常
#             self.initWebsocket()
#
#             self.reconnecting = False
#
#     # ----------------------------------------------------------------------
#     def connect(self, host, apiKey, secretKey, trace=False):
#         """连接"""
#         self.host = host
#         self.apiKey = apiKey
#         self.secretKey = secretKey
#
#         websocket.enableTrace(trace)
#
#         self.initWebsocket()
#         self.active = True
#
#     # ----------------------------------------------------------------------
#     def initWebsocket(self):
#         """"""
#         self.ws = websocket.WebSocketApp(self.host,
#                                          on_message=self.onMessageCallback,
#                                          on_error=self.onErrorCallback,
#                                          on_close=self.onCloseCallback,
#                                          on_open=self.onOpenCallback)
#
#         kwargs = {'sslopt': {'cert_reqs': ssl.CERT_NONE}}
#         self.wsThread = Thread(target=self.ws.run_forever, kwargs=kwargs)
#         self.wsThread.start()
#
#     # ----------------------------------------------------------------------
#     def readData(self, evt):
#         """解码推送收到的数据"""
#         # 先解压
#         decompress = zlib.decompressobj(-zlib.MAX_WBITS)
#         inflated = decompress.decompress(evt)
#         inflated += decompress.flush()
#
#         # 再转换为json
#         data = json.loads(inflated)
#         return data
#
#     # ----------------------------------------------------------------------
#     def closeHeartbeat(self):
#         """关闭接口"""
#         if self.heartbeatThread and self.heartbeatThread.isAlive():
#             self.active = False
#             self.heartbeatThread.join()
#
#     # ----------------------------------------------------------------------
#     def closeWebsocket(self):
#         """关闭WS"""
#         if self.wsThread and self.wsThread.isAlive():
#             self.ws.close()
#             self.wsThread.join()
#
#     # ----------------------------------------------------------------------
#     def close(self):
#         """"""
#         self.closeHeartbeat()
#         self.closeWebsocket()
#
#     # ----------------------------------------------------------------------
#     def onMessage(self, data):
#         """信息推送"""
#         print('onMessage')
#         print(data)
#
#     # ----------------------------------------------------------------------
#     def onError(self, data):
#         """错误推送"""
#         print('onError')
#         print(data)
#
#     # ----------------------------------------------------------------------
#     def onClose(self):
#         """接口断开"""
#         print('onClose')
#
#     # ----------------------------------------------------------------------
#     def onOpen(self):
#         """接口打开"""
#         print('onOpen')
#
#     # ----------------------------------------------------------------------
#     def onMessageCallback(self, ws, evt):
#         """"""
#         data = self.readData(evt)
#         if 'event' in data:
#             self.heartbeatReceived = True
#         else:
#             self.onMessage(data[0])
#
#     # ----------------------------------------------------------------------
#     def onErrorCallback(self, ws, evt):
#         """"""
#         self.onError(evt)
#
#     # ----------------------------------------------------------------------
#     def onCloseCallback(self, ws):
#         """"""
#         self.onClose()
#
#     # ----------------------------------------------------------------------
#     def onOpenCallback(self, ws):
#         """"""
#         if not self.heartbeatThread:
#             self.heartbeatThread = Thread(target=self.heartbeat)
#             self.heartbeatThread.start()
#
#         self.onOpen()
#
#     # ----------------------------------------------------------------------
#     def generateSign(self, params):
#         """生成签名"""
#         l = []
#         for key in sorted(params.keys()):
#             l.append('%s=%s' % (key, params[key]))
#         l.append('secret_key=%s' % self.secretKey)
#         sign = '&'.join(l)
#         return hashlib.md5(sign.encode('utf-8')).hexdigest().upper()
#
#     # ----------------------------------------------------------------------
#     def sendRequest(self, channel, params=None):
#         """发送请求"""
#         # 生成请求
#         d = {}
#         d['event'] = 'addChannel'
#         d['channel'] = channel
#
#         # 如果有参数，在参数字典中加上api_key和签名字段
#         if params is not None:
#             params['api_key'] = self.apiKey
#             params['sign'] = self.generateSign(params)
#             d['parameters'] = params
#
#         # 使用json打包并发送
#         j = json.dumps(d)
#
#         # 若触发异常则重连
#         try:
#             self.ws.send(j)
#             return True
#         except websocket.WebSocketConnectionClosedException:
#             self.reconnect()
#             return False
#
#     # ----------------------------------------------------------------------
#     def login(self):
#         params = {}
#         params['api_key'] = self.apiKey
#         params['sign'] = self.generateSign(params)
#
#         # 生成请求
#         d = {}
#         d['event'] = 'login'
#         d['parameters'] = params
#         j = json.dumps(d)
#
#         # 若触发异常则重连
#         try:
#             self.ws.send(j)
#             return True
#         except websocket.WebSocketConnectionClosedException:
#             self.reconnect()
#             return False