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

df = pd.read_csv('sleep.csv')
df['age'] = df['age'].astype('int16')
print(df.dtypes)
df['gender'] = df['gender'].astype('category')
print(df.gender)
df['is_male'] = df['gender'].map({'Female': True, 'Male': False})
print(df.is_male)

# Example4:
data ={
    'ID': [1,2],
    'name': ['alice smith', 'bob smith'],
    'Math': [90,85],
    'English': [88,92],
    'Science': [95,89]
}
df = pd.DataFrame(data)
print(df)
#    ID   name  Math  English  Science
# 0   1  alice    90       88       95
# 1   2    bob    85       92       89
# df.T
# Convert broad table to long table
df2 = pd.melt(df, id_vars=['ID', 'name'], var_name='Subject', value_name='Score')
df2.sort_values('name')
print(df2)
# Convert long table to broad table
df3 = pd.pivot(df2, index=['ID','name'], columns='Subject', values='Score')
print(df3)
# Subject   English  Math  Science
# ID name
# 1  alice       88    90       95
# 2  bob         92    85       89
# print(df3)
# df3 = pd.pivot(df2, index=['ID','name'], columns='Score', values='Subject')
# Score       85       88       89    90       92       95
# ID name
# 1  alice   NaN  English      NaN  Math      NaN  Science
# 2  bob    Math      NaN  Science   NaN  English      NaN

# Split columns
df[['first','last']] = df['name'].str.split(' ', expand=True)
print(df)
#    ID         name  Math  English  Science  first   last
# 0   1  alice smith    90       88       95  alice  smith
# 1   2    bob smith    85       92       89    bob  smith
df = pd.read_csv('sleep.csv')
print(df.head())

df = df[['person_id', 'blood_pressure']]
print(df)
# blood_pressure: 124/89
df[['high', 'low']] = df['blood_pressure'].str.split('/', expand=True)
print(df)
# Default type of new column is [object]
df['high'] = df['high'].astype('int64')
df['low'] = df['low'].astype('int64')
print(df.info())

# Data Box sealing: pd.cut(x, bins, labels)
df = pd.read_csv('employees.csv')
print(df.head(10))
df1 = df.head(10)[['employee_id', 'salary']]
print(df1)

df2 = pd.cut(df1['salary'], bins=2).value_counts()
# Split scopes: 4180.2 - 14100.0 - 24000.0
# 0    (14100.0, 24000.0]
# 1    (14100.0, 24000.0]
# 2    (14100.0, 24000.0]
# 3     (4180.2, 14100.0]
# 4     (4180.2, 14100.0]
# 5     (4180.2, 14100.0]
# 6     (4180.2, 14100.0]
# 7     (4180.2, 14100.0]
# 8     (4180.2, 14100.0]
# 9     (4180.2, 14100.0]

print(df2)
# Use value_counts() to classify result
# (4180.2, 14100.0]     7
# (14100.0, 24000.0]    3
df1['SalaryScope'] = pd.cut(df1['salary'], bins=[0, 10000, 20000, 30000], labels=['Low', 'Medium', 'High']) # .value_counts()
print(df1)
# salary
# (0, 10000]        6
# (10000, 20000]    3
# (20000, 30000]    1

df5= pd.qcut(df1['salary'], 3).value_counts()
print(df5)
# salary
# (12000.0, 24000.0]    4
# (4199.999, 6000.0]    3
# (6000.0, 12000.0]     3

df = pd.read_csv('sleep.csv')
df1 = df.head(10)[['person_id', 'sleep_quality', 'gender']]
print(df1)
df1['SleepQuality'] = pd.cut(df1['sleep_quality'], bins=3, labels=['Bad', 'Medium', 'Good'])
print(df1)
print(df1['SleepQuality'].value_counts())
# SleepQuality
# Medium    5
# Bad       3
# Good      2

# String -> classify -> statistics
# Value -> DataBoxing -> statistics
df['gender'] = df['gender'].astype('category')
print(df['gender'].value_counts())
# [category] type
print(df1['SleepQuality'].dtypes)

# df.rename(),df.set_index(),df.reset_index()
df = pd.DataFrame(
    {
        'name': ['Tom', 'Jerry', 'Jim', 'James'],
        'age': [18,19,18,20],
        'gender': ['Male', 'Female', 'Male', 'Male'],
    })
df.set_index('name', inplace=True)
print(df)
df.reset_index(inplace=True)
print(df)
df.rename(columns={'age': 'AGE'}, index={0:4}, inplace=True)
print(df)
df.index=[1,2,3,4]
df.columns=['Name', 'Age', 'Gender']
print(df)