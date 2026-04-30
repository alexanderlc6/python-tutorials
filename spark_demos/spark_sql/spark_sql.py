from pyspark.sql import SparkSession

if __name__ == '__main__':
    spark = SparkSession.builder.appName('test').master('local[*]').config('spark.serializer', 'org.apache.spark.serializer.KryoSerializer') \
        .config('spark.kryoserializer.buffer.max', '512m') \
        .config('spark.executor.extraJavaOptions', '-Dio.netty.tryReflectionSetAccessible=true') \
        .config('spark.driver.extraJavaOptions', '-Dio.netty.tryReflectionSetAccessible=true') \
        .getOrCreate()
    sc = spark.sparkContext

    df = spark.read.csv('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/stu_score.txt',
                        schema='id INT, subject STRING, score INT')

    df.createTempView('score')
    df.createOrReplaceTempView('score_2')
    df.createGlobalTempView('score_3')

    spark.sql('select subject, count(*) as cnt from score group by subject').show()
    spark.sql('select subject, count(*) as cnt from score_2 group by subject').show()
    spark.sql('select subject, count(*) as cnt from global_temp.score_3 group by subject').show()
