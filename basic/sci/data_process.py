import pandas as pd
df1 = pd.DataFrame({'A': [1], 'B': [2]})
df2 = pd.DataFrame({'A': [3], 'B': [4]})
# Method 1
result = pd.concat([df1, df2], ignore_index=True)
print(result)
# Method 2
result = df1.append(df2, ignore_index=True)
print(result)

