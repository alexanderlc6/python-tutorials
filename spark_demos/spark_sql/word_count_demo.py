from pyspark.sql import SparkSession
from pyspark.sql import functions as F

if __name__ == '__main__':
    spark = SparkSession.builder.appName('test').master('local[*]').config('spark.serializer', 'org.apache.spark.serializer.KryoSerializer') \
        .config('spark.kryoserializer.buffer.max', '512m') \
        .config('spark.executor.extraJavaOptions', '-Dio.netty.tryReflectionSetAccessible=true') \
        .config('spark.driver.extraJavaOptions', '-Dio.netty.tryReflectionSetAccessible=true') \
        .getOrCreate()
    sc = spark.sparkContext

    # SQL style
    rdd = sc.textFile('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/words.txt')\
        .flatMap(lambda x : x.split(' ')) \
        .map(lambda x: [x])
    df = rdd.toDF(['word'])
    df.createTempView('words')
    spark.sql('select word, count(*) as cnt from words group by word order by cnt desc').show()

    # DSL style
    df = spark.read.text('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/words.txt')
    df2 = df.withColumn('value', F.explode(F.split(df['value'], ' ')))
    df2.groupby('value').count().withColumnRenamed('value', 'word').withColumnRenamed('count','cnt')\
        .orderBy('cnt', ascending=False)\
        .show()