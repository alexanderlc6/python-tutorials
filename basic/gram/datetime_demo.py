import pandas as pd
d = pd.Timestamp('2022-03-15 10:22')
d1 = pd.Timestamp('2022-03-15 14:32')
print(d)
print(type(d))
print('Year:', d.year)
print('Month:', d.month)
print('Day:', d.day)
print(d.hour,d.minute,d.second)
print('Quarter:', d.quarter)
print('End of month?', d.is_month_end)

print('Week day:', d.day_name())
print('Convert to day:', d.to_period('D'))
print('Convert to day:', d1.to_period('D'))
print('Convert to quarter:', d1.to_period('Q'))
print('Convert to year:', d1.to_period('Y'))
print('Convert to month:', d1.to_period('M'))
print('Convert to week:', d1.to_period('W'))

a = pd.to_datetime(d)
a = pd.to_datetime('20260201')
print(a)
print(type(a), a.day_name())

df = pd.DataFrame({
    'sales': [100,200,300],
    'date': ['20240201','20240202','20240203']
})
df['datetime'] = pd.to_datetime(df['date'])
print(df)
# datetime64[ns]
print(df.info())
# Series type
print(type(df['datetime']))
df['Weekday'] = df['datetime'].dt.day_name()
print(df)
print(df['datetime'].dt.year)

# CSV file
df = pd.read_csv('weather.csv', parse_dates=['date'])
print(df)
df['datetime'] = pd.to_datetime(df['date'])
print(df)
print(df['datetime'].dt.day_name())
print(df['date'].dt.day_name())

# Date data as index and query time scope data
df.set_index('date',inplace=True)
print(df.loc['2013-01':'2013-02'])

# Time interval
d1 = pd.Timestamp('2013-01-15')
d2 = pd.Timestamp('2023-02-23')
d3 = d2 - d1
print(d3)
print(type(d3))

df = pd.read_csv('weather.csv', parse_dates=['date'])
print(df)
df['delta'] = df['date'] - df['date'][0]
df.set_index('delta', inplace=True)
print(df)
print(df.loc['10 days':'20 days'])

# Time sequence
# days = pd.date_range('2025-01-01','2025-03-06', freq='W')
# D,Q,W,YS,YE
days = pd.date_range('2025-01-01', periods=10, freq='W')
print(days)

# Resampling: get yearly average temperature
df = pd.read_csv('weather.csv', parse_dates=['date'])
print(df)
df.set_index('date', inplace=True)
print(df[['temp_max', 'temp_min']].resample('YE').mean())