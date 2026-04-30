import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StringType, IntegerType

if __name__ == '__main__':
    spark = SparkSession.builder.appName('test').master('local[*]') \
        .config('spark.sql.shuffle.partitions', 2) \
        .getOrCreate()
        # .config('spark.serializer', 'org.apache.spark.serializer.KryoSerializer') \
        # .config('spark.kryoserializer.buffer.max', '512m') \
        # .config('spark.executor.extraJavaOptions', '-Dio.netty.tryReflectionSetAccessible=true') \
        # .config('spark.driver.extraJavaOptions', '-Dio.netty.tryReflectionSetAccessible=true') \


    sc = spark.sparkContext

    schema = StructType().add('user_id', StringType(), nullable=True)\
                .add('movie_id', IntegerType(), nullable=True)\
                .add('rank', IntegerType(), nullable=True)\
                .add('ts', StringType(), nullable=True)
    df = spark.read.csv('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/u.data',
                   sep='\t', header=False,encoding='utf-8', schema=schema)

    # Query users' average score
    df.groupby('user_id').avg('rank').withColumnRenamed('avg(rank)', 'avg_rank')\
        .withColumn('avg_rank', F.round('avg_rank', 2))\
        .orderBy('avg_rank', ascending=False)\
        .show()

    # Query movies' average score
    df.createTempView('movie')
    spark.sql('''
        select movie_id, round(avg(rank),2) as avg_rank from movie group by movie_id order by avg_rank desc
    ''').show()

    # Query movies count higher than average score
    print('Movies count higher than average score:', df.where(df['rank'] > df.select(F.avg(df['rank'])).first()['avg(rank)']).count())

    # Query most scoring user's average score in high score movies(score > 3)
    user_id = df.where('rank > 3').groupby('user_id').count().withColumnRenamed('count', 'cnt').orderBy('cnt', ascending=False)\
        .limit(1).first()['user_id']
    df.filter(df['user_id'] == user_id).select(F.round(F.avg('rank'), 2)).show()

    # Query each users' average score, max score and min score
    # agg(): API of GroupedData, support multiple aggregate functions
    df.groupby('user_id').agg(F.round(F.avg('rank'), 2).alias('avg_rank'),
                              F.min('rank').alias('min_rank'),
                              F.max('rank').alias('max_rank')
                              ).show()

    # Query top 10 average score movies which evaluated more than 100 times
    df.groupby('movie_id').agg(
        F.count('movie_id').alias('cnt'),
        F.round(F.avg('rank'), 2).alias('avg_rank')
    ).where('cnt > 100')\
    .orderBy('avg_rank', ascending=False)\
    .limit(10)\
    .show()

    # | movie_id | cnt | avg_rank |
    # +--------+---+--------+
    # | 408 | 112 | 4.49 |
    # | 318 | 298 | 4.47 |
    # | 169 | 118 | 4.47 |
    # | 483 | 243 | 4.46 |
    # | 64 | 283 | 4.45 |
    # | 12 | 267 | 4.39 |
    # | 603 | 209 | 4.39 |
    # | 50 | 583 | 4.36 |
    # | 178 | 125 | 4.34 |
    # | 357 | 264 | 4.29 |
    # +--------+---+--------+

time.sleep(10000)