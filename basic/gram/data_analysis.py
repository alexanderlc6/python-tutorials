import json

import numpy as np
import pandas as pd
df = pd.read_csv('employees.csv')
print(df.head())
print(df['salary'].mean())

df = df.tail()
df.to_csv('new1.csv')

df = pd.read_json('test.json')
print(df)

with open('test.json') as f:
    data = json.load(f)

# {'users': [{'id': 1, 'name': '张三', 'age': 28, 'email': 'zhangsan@example.com', 'is_active': True, 'join_date': '2022-03-15'}, {'id': 2, 'name': '李四', 'age': 35, 'email': 'lisi@example.com', 'is_active': False, 'join_date': '2021-11-02'}, {'id': 3, 'name': '王五', 'age': 24, 'email': 'wangwu@example.com', 'is_active': True, 'join_date': '2023-01-20'}]}
print(data)
df = pd.DataFrame(data['users'])
print(df)
#    id name  age                 email  is_active   join_date
# 0   1   张三   28  zhangsan@example.com       True  2022-03-15
# 1   2   李四   35      lisi@example.com      False  2021-11-02
# 2   3   王五   24    wangwu@example.com       True  2023-01-20

s = pd.Series([12,25,np.nan, None, pd.NA])
df = pd.DataFrame([[12, pd.NA, 32], [2,3,5], [None, 4, 6]], columns=['a', 'b', 'c'])
print(s)
# Check NA
print(s.isna())
print(s.isnull())
print(df.isna())
print(df.isnull())
print(s.isna().sum())
print(df.isna().sum(axis=1))

print('----------')
print(s.dropna())
print(df.dropna())
print(df.dropna(how='all'))
# At least 2 non-NA, then reserve
print(df.dropna(thresh=2))
# Drop all columns contains NA
print(df.dropna(axis=1))
print(df.dropna(subset=['a']))

# Fill NA cell
df = pd.read_csv('weather_withna.csv')
print(df.head())
print(df.isna().sum())
# Fill with dict value
print(df.fillna({'temp_max': 20, 'wind': 2.5}).tail())
print(df.fillna(df[['temp_max', 'wind']].mean()).tail())
print(df.ffill().tail())
print(df.bfill().tail())

data = {
    "name": ['alice', 'alice', 'bob', 'alice', 'jack', 'bob'],
    "age": [26,25,30,25,35, 30],
    'city': ['NY', 'NY', 'LA', 'NY', 'SF', 'LA']
}
df = pd.DataFrame(data)
print(df)
print(df.duplicated())
print(df.drop_duplicates(subset=['name'], keep='last'))

# Data type conversion
df = pd.read_csv('sleep.csv')