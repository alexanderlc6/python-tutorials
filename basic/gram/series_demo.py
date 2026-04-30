import pandas as pd
import numpy as np

# Creation
s = pd.Series([1,2,3,4,5])
print(s)

# Define indexes
s1 = pd.Series([1,2,3,4,5], index = ['a', 'b', 'c', 'd', 'e'], name='Month')
print(s1)

# Create by dict format
s2 = pd.Series({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})
print(s2)
s3 = pd.Series(s1, index=['a', 'c'])
print(s3)

# Series attributes
print(s1.index)
print(s1.values)
print(s1.name, s1.shape, s1.ndim, s1.size, s1.dtype)
print(s1.loc['c'])
print(s1.iloc[1])
# Get index range
# b    2
# c    3
# d    4
print(s1.loc['b':'d'])
print(s1.iloc[1:4])

print(s1.at['b'])
print(s1.iat[2])

# Access data
print(s[1])
print(s1['c'])

print(s1[s1<3])
s1['f']=6
print('head:', s1.head(1))
print('tail:', s1.tail(3))

s = pd.Series([10, 2, 3, np.nan, None, 4, 5], index = ['a', 'b', 'c', 'd', 'e', 'f', 'g'], name='data')
print(s)
print(s.head(3))
print(s.tail(5))
print(s.describe())
print(s.count())
print(s.keys(), s.index)
print(s.isna())

print(s.isin([4,5,6]))
print(s.mean())
print(s.std())
print(s.var())
print(s.min())
print(s.max())
print(s.median())
print(s.sort_values())
print(s.quantile(0.25))

print(s.quantile(0.8))

s['h'] = 4
print(s.mode())
print(s.value_counts())

print(s.drop_duplicates())
print(s.unique())
print(s.nunique())

# Value, index sort
print(s.sort_index())
print(s.sort_values())

# Example1: Find out students whose score greater than average score
np.random.seed(42)
values = np.random.randint(50, 101, 10)
index = ['Student' + str(i) for i in range(1,11)]
scores = pd.Series(values, index=index, name='Scores')
print(scores.mean(), scores.max(), scores.min())
mean = scores.mean()
print('Result:', len(scores[scores > mean]))
print('Result:', scores[scores > mean].count())

# Example2: Find out days more than 30 degree and temperature scope changes biggest 2 days
temps = pd.Series([28, 31, 29, 32, 30, 27, 33], index=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
print(len(temps[temps > 30]))
print(temps.mean())
print(temps.sort_values(ascending=False))
t1 = temps.diff().abs()
print('Temperature scope changes biggest 2 days:', t1.sort_values(ascending=False).keys()[:2].tolist())
print('Temperature scope changes biggest 2 days:', t1.sort_values(ascending=False).index[:2].tolist())

# Example3: Stock transaction price
prices = pd.Series([102.3,103.5,105.1,104.8,106.2,107.0,106.5,108.1,109.3,110.2], index=pd.date_range('2023-01-01', periods=10))
print(prices)
a = prices.pct_change()
print(a)
print(a.idxmax())
print(a.idxmin())
print(a.std())

# Example4:
a = pd.date_range('2022-01-01',periods=12,freq='MS')
print(a)
sales = pd.Series([120,135,145,160,155,170,180,175,190,200,210,220],index=a)
print(sales)
# Statistics by quarter(QS) or year(YS)
print(sales.resample('QS').mean())
print('Largest sales amount month:', sales.idxmax())
# Monthly increasement ratio
a = sales.pct_change()
print(a)
# Find out month of amount increased continuously over 2 month
b = a > 0
print(b[b.rolling(3).sum() == 3].keys().tolist())


# Example5:
np.random.seed(42)
hourly_sales = pd.Series(np.random.randint(0,100,24),
                         index=pd.date_range('2025-01-01', periods=24, freq='h'))
print(hourly_sales)

daily_sales = hourly_sales.resample('D').sum()
print(daily_sales)
print(hourly_sales.sum())

# Use:
print(hourly_sales.between_time('08:00', '22:00'))
# Or use:
mask = (hourly_sales.index.hour >= 8) & (hourly_sales.index.hour <= 22)
biz_time_sales = hourly_sales[mask]
non_biz_time_sales = hourly_sales.drop(biz_time_sales.index)
# Or use:
non_biz_time_sales = hourly_sales[~mask]
print('non_biz_time_sales:', non_biz_time_sales)
print(biz_time_sales.sum() / (daily_sales - biz_time_sales.sum()))
print(biz_time_sales.sum() / non_biz_time_sales.sum())
print(hourly_sales.nlargest(3).keys())