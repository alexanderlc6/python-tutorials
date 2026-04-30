from pyspark.sql import SparkSession
import os


if __name__ == '__main__':
    spark = SparkSession.builder.appName('test').master('local[*]').config('spark.serializer', 'org.apache.spark.serializer.KryoSerializer') \
        .config('spark.kryoserializer.buffer.max', '512m') \
        .config('spark.executor.extraJavaOptions', '-Dio.netty.tryReflectionSetAccessible=true') \
        .config('spark.driver.extraJavaOptions', '-Dio.netty.tryReflectionSetAccessible=true') \
        .getOrCreate()
    sc = spark.sparkContext

    # spark_df = spark.read.csv('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/stu_score.txt', sep=',', header=False)
    # actual_df = spark_df.toDF('id', 'name', 'score')
    # # Print table structure
    # actual_df.printSchema()
    # actual_df.show()
    #
    # actual_df.createTempView('score')
    #
    # # SQL style
    # spark.sql('''
    #     select * from score where name='语文' limit 5
    # ''').show()
    #
    # # DSL style
    # actual_df.where("name='语文'").limit(5).show()

    # Convert RDD to DataFrame
    rdd = sc.textFile('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/people.txt').\
        map(lambda x: x.split(',')).map(lambda x: (x[0], int(x[1])))
    # df = spark.createDataFrame(rdd, schema=['name', 'age'])
    # df.printSchema()
    # df.show(20, False)
    # df.createOrReplaceTempView('people')
    # spark.sql('select * from people where age < 30').show()

    from pyspark.sql.types import StructType, StringType, IntegerType
    schema = StructType().add('name', StringType(), nullable=True).add('age', IntegerType(), nullable=False)
    df = spark.createDataFrame(rdd, schema=schema)
    df.printSchema()
    df.show()

    # df1 = rdd.toDF(schema=['name', 'age'])
    df1 = rdd.toDF(schema=schema)
    df1.printSchema()
    df1.show()

    # Convert from pandas DataFrame
    import pandas as pd
    pdf = pd.DataFrame(
        {
            'id':[1,2,3],
            'name':['AA', 'BB', 'CC'],
            'age': [12,53,14]
        }
    )

    sdf = spark.createDataFrame(pdf)
    sdf.printSchema()
    sdf.show()

    # Build from union API
    schema = StructType().add('data', StringType(), nullable=True)
    # text_sdf1 = spark.read.format('text').schema(schema=schema).load('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/people.txt')
    text_sdf2 = spark.read.text('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/people.txt', wholetext=True)
    text_sdf2.printSchema()
    text_sdf2.show()

    # json_df1 = spark.read.format('json').load('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/people.json')
    json_df2 = spark.read.json('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/people.json')
    json_df2.printSchema()
    json_df2.show()

    # csv_df = spark.read.format('csv').option('sep',';').option('header', True).option('encoding', 'utf-8')\
    #     .schema('name STRING, age INT, job STRING')\
    #     .load('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/people.csv')
    # csv_df.printSchema()
    # csv_df.show()
    csv_df2= spark.read.csv('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/people.csv',
                            sep=';', schema='name STRING, age INT, job STRING', header=False, encoding='utf-8')
    csv_df2.printSchema()
    csv_df2.show()

    # Read parquet datasource
    pqt_df = spark.read.parquet('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/users.parquet')
    pqt_df.printSchema()
    pqt_df.show()