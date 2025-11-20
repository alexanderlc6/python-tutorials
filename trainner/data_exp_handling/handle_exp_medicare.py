import pandas as pd
data = pd.read_csv('medical_data.csv', encoding='gbk')

print(data.dtypes)
print(data.info())

# 显示每一列的空缺值数量
print(data.isnull().sum())

# 规范日期格式
data['就诊日期'] = pd.to_datetime(data['就诊日期'])
data['诊断日期'] = pd.to_datetime(data['诊断日期'])

# 修改列名
data.rename(columns={'病人ID':'患者ID'}, inplace=True)

# 查看修改后的表结构
print(data.info())

from datetime import datetime

# 增加诊断延迟和病程列
data['诊断延迟'] = (data['诊断日期'] - data['就诊日期']).dt.days
data['病程'] = (datetime(2024,9,1) - data['诊断日期']).dt.days

# 删除不合理的数据
data = data[(data['诊断延迟'] >= 0) & (data['病程'] >= 0) & (data['年龄'] < 120)]

# 查看修改后的数据
print(data.describe())

# 删除重复值并记录删除的行数
initial_rows = data.shape[0]
data.drop_duplicates(inplace=True)
deleted_rows = initial_rows - data.shape[0]
print(f'删除的重复行数:{deleted_rows}')

from sklearn.preprocessing import MinMaxScaler

# 归一化处理
scaler = MinMaxScaler()
columns_to_normalize = ['年龄','体重','身高']
data[columns_to_normalize] = scaler.fit_transform(data[columns_to_normalize])

# 查看归一化后的数据
print(data.head())

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 统计治疗结果分布
treatment_outcome_distribution = data.groupby('疾病类型')['治疗结果'].value_counts().unstack()

# 设置中文字体
font_path = 'C:/Windows/Fonts/simhei.ttf'
my_font = fm.FontProperties(fname=font_path)

# 绘制柱状图
treatment_outcome_distribution.plot(kind='bar', stacked=True)
plt.title('不同疾病类型的治疗结果分布', fontproperties=my_font)
plt.xlabel('疾病类型', fontproperties=my_font)
plt.ylabel('治疗结果数量', fontproperties=my_font)
# 设置x轴刻度标签的字体
plt.xticks(fontproperties=my_font)
# 设置y轴刻度标签的字体
plt.yticks(fontproperties=my_font)
# 设置图例字体
plt.legend(prop=my_font)
plt.show()

# 绘制散点图
plt.scatter(data['年龄'],data['疾病严重程度'])
plt.title('年龄和疾病严重程度的关系', fontproperties=my_font)
plt.xlabel('年龄', fontproperties=my_font)
plt.ylabel('疾病严重程度', fontproperties=my_font)
# 设置x轴刻度标签的字体
plt.xticks(fontproperties=my_font)
# 设置y轴刻度标签的字体
plt.yticks(fontproperties=my_font)
# 设置图例字体
plt.legend(prop=my_font)
plt.show()

# 保存处理后的数据
data.to_csv('cleaned_medicare_data.csv', index=False)