import datetime
import pandas as pd
start_date = datetime.datetime(2017, 7, 1,0,0)
print(type(start_date))
print(str(start_date))

df = pd.read_csv('D:\coin_quant_ class_0518\coin_quant_class\data\eos1m.csv')
print(type(df['candle_begin_time']))
df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'])

print(df.info())