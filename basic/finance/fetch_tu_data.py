import datetime

import tushare as ts
import pandas as pd

# Tushare-pro version usages
# ts.set_token('ecad521ae665fb86e461e8f799290104e36971ab25243b50bf36b4d2')
# pro = ts.pro_api()
# print(datetime.date.today())
end_date = datetime.date.today().strftime('%Y-%m-%d')

# try:
#     df = pro.query('trade_cal', exchange='', start_date='20251001', end_date=end_date,
#                    fields='exchange,cal_date,is_open,pretrade_date', is_open='0')
#     df['date'] = pd.to_datetime(df['date'])
#     df = df.set_index('date')[['close']]
#     print(f'Get query timescope:{df.index.min()} ~ {df.index.max()}, length is:' + {len(df)})
#     print(df.head())
#
#     # Upper integral data
#     df.to_csv('600000.csv')
#     df = pd.read_csv('600000.csv', header = 0, index_col = 'data')[['close']]
# except Exception as e:
#     print(f'Error:{e}')

# Tushare old version usages
df = ts.get_k_data('600000', '2025-10-01', end_date)
df.to_csv('600000.csv')
df = pd.read_csv('600000.csv', header = 0, index_col = 'date')[['close']]

df1 = ts.get_k_data('000980', '2025-10-01', end_date)
df1.to_csv('000980.csv')
df1 = pd.read_csv('000980.csv', header = 0, index_col = 'date')[['close']]

df2 = ts.get_k_data('000981', '2025-10-01', end_date)
df2.to_csv('000981.csv')
df2 = pd.read_csv('000981.csv', header = 0, index_col = 'date')[['close']]

df = df.reset_index()
df1 = df1.reset_index()
df2 = df2.reset_index()

a = pd.merge(left = df, right = df1, left_on='date', right_on='date')
b = pd.merge(left = a, right = df2, left_on='date', right_on='date')
c = b.set_index('date')
c.columns = ['600000', '000980', '000981']
# Front and tail records
print(c.head())
print(c.tail())

# Get column data
print('====Get column data====')
data = c[['600000', '000981']]
data.head()
print(data)

# Check rows and columns count
print(data.shape)

# Get row 2~4 data
print('====Get row 2~4 data====')
data.iloc[1:4]
print(data)

# Get row 1~2, column 1~3 data
print('====Get row 1~2, column 1~3 data====')
data.iloc[:2, :3]
print(data)
# Tushare-pro version usages
import tushare as ts
# ts.set_token('ecad521ae665fb86e461e8f799290104e36971ab25243b50bf36b4d2')
# pro = ts.pro_api()
# df = pro.user(token='ecad521ae665fb86e461e8f799290104e36971ab25243b50bf36b4d2')
# print(df)

# df = pro.query('trade_cal', exchange='000875', start_date='20251001', end_date='20251024',
#                fields='exchange,cal_date,is_open,pretrade_date', is_open='0')

# df = ts.get_k_data('000875')
# df.to_csv('000875.csv')
# df.to_csv('000875-part.csv', columns=['open','high','low','close'])
