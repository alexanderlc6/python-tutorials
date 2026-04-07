import pandas as pd

# Creation
s1 = pd.Series([1,2,3,4,5])
s2 = pd.Series([6,7,8,9,10])
df = pd.DataFrame({'col1': s1, 'col2': s2})
print(df)
print(type(df['col1']))

df = pd.DataFrame(
    {
        'name': ['Tom', 'Jerry', 'Tom','Mike', 'Jim', 'James'],
        'age': [18,19,18,20,18, 25],
        'score': [80,85,80,90,95,80],
    },index=[1,2,3,4,5,6],
    columns=['name', 'score', 'age']
)
print(df)

print(df.index)
print('Columns:', df.columns)
print(df.values)
print(df.ndim, df.dtypes, df.shape, df.size)
print(df.T)
print(df.T.index, df.T.columns, df.T.shape)

# Get element
print(df.loc[4])
print(df.iloc[3])

print(df.loc[:, 'name'])
print(df.iloc[:, 0])
print(df.at[3, 'score'])
print(df.iat[2, 1])
print(df.loc[3, 'score'])
print(df.iloc[2, 1])

# Get a column
print(df['name'])
print(df.name)
print(df[['name', 'score']]) #DataFrame

# Get partial data
print(df.head(2))
print(df.tail(3))
# Use bool index to filter
print(df[(df.score>70) & (df.age < 20)])

# Random sampling
print(df.sample(3))

print(df.isin(['James', 20]))
print(df.isna())
print(df['score'].sum())
print(df.score.max())
print(df.age.min())
print(df.score.mean())
print(df.score.median())
print(df.age.mode())

print(df.score.std())
print(df.score.var())
print(df.score.quantile(0.25))
print(df.describe())

print(df.count())
print(df.value_counts())
print(df.drop_duplicates())
print(df.duplicated(subset=['age']))

print(df.sample(3))
print(df.replace(18, 40))

print(df)
print(df.cumsum())
print(df.cummax())
print(df.cummin(axis=0))

print(df.sort_index(ascending=False))
print(df.sort_values(by=['score','age'], ascending=False))
print(df.nlargest(2, columns=['score', 'age']))
print(df.nsmallest(2, columns=['score', 'age']))

# Example1
data ={
    'Name': ['AA','BB','CC','DD','EE'],
    'Math': [85, 92, 78,88, 95],
    'English': [90, 88, 85, 92, 80],
    'Physics': [75, 80, 88, 85, 90]
}

scores = pd.DataFrame(data)
print(scores)
scores['TotalScore'] = scores[['Math', 'English', 'Physics']].sum(axis=1)
print(scores)
scores['AvgScore'] = scores['TotalScore'] / 3
scores['AvgScore2'] = scores[['Math', 'English', 'Physics']].mean(axis=1)
print(scores)

print(scores[(scores['Math']>90) | (scores['English'] > 85)])
df2 = scores.sort_values('TotalScore', ascending=False).head(3)
print(df2)
print(scores.nlargest(3, columns=['TotalScore']))

# Example2
data = {
            'Product': ['A','B','C','D'],
            'Price': [100, 150, 200, 120],
            'Sales': [50, 30, 20, 40]
    }
df = pd.DataFrame(data)
df['TotalSales'] = df['Price'] * df['Sales']
print(df)
print(df.nlargest(1, columns=['TotalSales']))
print(df.sort_values('TotalSales', ascending=False))

# Example3
data = {
    '用户ID': [101,102,103,104,105],
    '用户名':['Alice','Bob','charlie','David','Eve'],
    '商品类别':['电子产品','服饰','电子产品','家居','服饰'],
    '商品单价':[1200,308,800,150,200],
    '购买数量':[1,3,2,5,4]
}

df = pd.DataFrame(data)
print(df)
df['总消费金额'] = df['商品单价'] * df['购买数量']
print(df)
print(df.nlargest(1, columns=['总消费金额']))
print(df['总消费金额'].mean())

print(df[df['商品类别'] == '电子产品']['购买数量'].sum())
