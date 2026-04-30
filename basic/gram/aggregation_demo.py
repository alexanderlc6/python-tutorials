import pandas as pd

df = pd.read_csv('employees.csv')
print(df)
print(df['department_id'].isna().sum())
df = df.dropna(subset=['department_id'])
df['department_id'] = df['department_id'].astype('int64')
print(df)

# Calculate average salary of each department
print(df.groupby('department_id').groups)
print(df.groupby('department_id').get_group(20))
df2 = df.groupby('department_id')[['salary']].mean()
df2['salary'] = df2['salary'].round(2)
df2.reset_index(inplace=True)
df2 = df2.sort_values('salary', ascending=False)
print(df2)

# Each position in each departments
df2 = df.groupby(['department_id', 'job_id'])[['salary']].mean()
df2.reset_index(inplace=True)
df2['salary'] = df2['salary'].round(1)
df2.sort_values('salary', ascending=False, inplace= True)
print(df2)

# =========================================
import pandas as pd
df = pd.read_csv('penguins.csv')
df.head(5)
print(df.info())
print(df.isna().sum())
df.dropna(inplace=True)
print(df.isna().sum())
print(len(df))

df['sex'] = df['sex'].astype('category')
df['bill_ratio'] = df['bill_length_mm'] / df['bill_depth_mm']
print(df)

labels = ['Low', 'Medium', 'High']
df['mass_level'] = pd.cut(df['body_mass_g'], bins=3, labels=labels)
print(df['mass_level'].value_counts())

df = df.groupby(['sex', 'island']).agg({
    'body_mass_g': ['mean', 'count']
})
print(df)


# Example2
df = pd.read_csv('sleep.csv')
print(df.head())
df.info()
print(df.describe())

print(df.isna().sum())

print(df['sleep_disorder'].value_counts())
# sleep_disorder
# Insomnia       79
# Sleep Apnea    31
# Name: count, dtype: int64
df.drop(columns=['sleep_disorder'], inplace= True)
print(df.head())
print(df.isna().sum())

df['gender'] = df['gender'].astype('category')
print(df['occupation'].value_counts())
df['occupation'] = df['occupation'].astype('category')
df['bmi_category'] = df['bmi_category'].astype('category')
df[['High', 'Low']] = df['blood_pressure'].str.split('/', expand=True)
print(df.head())

labels=['Bad', 'Medium', 'Good']
df['quality_level'] = pd.cut(df['sleep_quality'], bins=3, labels=labels)
print(df)
age_levels = ['Junior', 'Young', 'Old']
df['age_level'] = pd.cut(df['age'], bins=3, labels=age_levels)
print(df.head())

print(df['bmi_category'].value_counts())
print(df.groupby(['age_level', 'bmi_category']).agg({
    'sleep_duration': 'mean',
    'sleep_quality': 'mean',
    'stress_level': 'mean'
}))
