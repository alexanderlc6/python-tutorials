# Read CSV file
import pandas as pd
a = ['apple', 'pear', 'watch', 'money']
b = [[1,2,3,4,5],[5,7,8,9,0],[2,1,4,5,6],[3,5,2,5,6]]
d = dict(zip(a, b))
print(d)
p = pd.DataFrame(d)
print(p)
p.to_csv('../../data_files/test_output.csv')
pd.read_csv('../../resources/test_output.csv')

# Read Excel data
import numpy as np
df = pd.read_excel('../../data_files/test_data_read.xlsx')
print(df.head())

data = pd.DataFrame(df)
data.head()
# Set Z1 as var X, set Z2 as var Y
X = np.array(data['Z1'])
Y = np.array(data['Z2'])
print('Rows:{0},{1}'.format(X.shape, Y.shape))

# Divide into 2 types by amount
data['AmountType'] = np.where(data['Z1'] > 35, 'High', 'Low')
print(data['AmountType'])
type_amt_count = data['AmountType'].value_counts()
high_amt_ratio = type_amt_count['High'] / len(data)
low_amt_ratio = type_amt_count['Low'] / len(data)

print('High amount ratio:', high_amt_ratio)
print('Low amount ratio:', low_amt_ratio)

# Grouping statistics
amt_bins = [0, 30, 60, 80, 100, np.inf]
amt_labels = ['T1', 'T2', 'T3', 'T4', 'T5']
data['AmtTypeRange'] = pd.cut(data['K'], bins=amt_bins, labels=amt_labels, right=False)
amt_rate = data.groupby('AmtTypeRange')['AmountType'].apply(lambda x: (x == 'High').mean())
amt_count = data.value_counts()
print('Amt K area - High ratio is:', amt_rate)
print('Amt K area count', amt_count)




