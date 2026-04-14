import os
import subprocess

from pyspark.sql import functions as F
from pyspark.shell import spark
# Use spark session instead of pyspark.shell
from pyspark.sql import SparkSession

# java17_path = subprocess.check_output(["/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home", '-v','17']).decode("utf-8").strip()
# os.environ["JAVA_HOME"] = java17_path
# os.environ['PATH'] = f"{java17_path}/bin:{os.environ.get('PATH', '')}"

df = spark.read.json('test1.json')
# df.where('age > 20').select('name.first').show()

# Refactoring code
df.printSchema()
df.show(truncate=False)
if 'age' in df.columns:
    df.where('age > 20').select('name.first_name').show()
else:
    print(f'Useful columns:{df.columns}')

# Use spark session instead of pyspark.shell
sparkObj = SparkSession.builder.appName("test").getOrCreate()
rdd = sparkObj.sparkContext.textFile('test1.json')
result = rdd.flatMap(lambda line: line.split(' ')).map(lambda word:(word, 1)).reduceByKey(lambda a,b: a+b).collect()
df = spark.read.json('test1.json')
df.filter(df.age > 18).groupby('dept').agg(F.sum('salary').alias('total_salary')).orderBy(F.desc('total_salary')).show()

# df = sparkObj.read.json('test1.json')
# df.filter(df.age > 16).groupby('dept').agg(F.sum('salary').alias('total_salary')).orderBy(F.desc('total_salary')).show()