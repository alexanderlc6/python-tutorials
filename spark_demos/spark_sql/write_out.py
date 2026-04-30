from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StringType, IntegerType

if __name__ == '__main__':
    spark = SparkSession.builder.appName('test').master('local[*]').config('spark.serializer', 'org.apache.spark.serializer.KryoSerializer') \
        .config('spark.kryoserializer.buffer.max', '512m') \
        .config('spark.executor.extraJavaOptions', '-Dio.netty.tryReflectionSetAccessible=true') \
        .config('spark.driver.extraJavaOptions', '-Dio.netty.tryReflectionSetAccessible=true') \
        .getOrCreate()
    sc = spark.sparkContext

    schema = StructType().add('user_id', StringType(), nullable=True)\
                .add('movie_id', IntegerType(), nullable=True)\
                .add('rank', IntegerType(), nullable=True)\
                .add('ts', StringType(), nullable=True)
    df = spark.read.csv('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/u.data',
                   sep='\t', header=False,encoding='utf-8', schema=schema)

    # Write to text(single column)
    df.select(F.concat_ws('...', 'user_id', 'movie_id', 'rank', 'ts')).write.mode('overwrite')\
        .text('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/output/chg_text')

    df.write.mode('overwrite').csv('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/output/chg_csv', sep=';', header=True)
    df.write.mode('overwrite').json('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/output/chg_json')
    df.write.mode('overwrite').parquet(
        'file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/chg_parquet')

    # Write to DB and read out
    df.write.mode('overwrite').jdbc(url='jdbc:mysql://localhost:3306?bigdata?useSSL=false&useUnicode=true',
                                    table='movies', properties={'user':'root', 'password': '123456'})
    df2= spark.read.jdbc(url='jdbc:mysql://localhost:3306?bigdata?useSSL=false&useUnicode=true',
                                    table='movies', properties={'user':'root', 'password': '123456'})
    df2.printSchema()
    df2.show()