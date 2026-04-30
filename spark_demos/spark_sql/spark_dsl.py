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

    # Query API
    # df.select(['id', 'subject']).show()
    # df.select(df['id'], df['subject']).show()
    df.select('id', 'subject').show()

    # Filter API
    # df.filter('score < 99').show()
    df.filter(df['score'] < 99).show()

    # Where API
    # df.where('score < 99').show()
    df.where(df['score'] < 99).show()

    # Groupby API
    df.groupby('subject').count().show()
    # df.groupby(df['subject']).count().show()

    r = df.groupby('subject')
    # Return [GroupedData] type
    print('grouby return object type:', type(r))
    r.sum().show()