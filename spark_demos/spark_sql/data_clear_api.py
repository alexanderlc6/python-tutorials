from pyspark.sql import SparkSession

if __name__ == '__main__':
    spark = SparkSession.builder.appName('test').master('local[*]')\
        .getOrCreate()
    sc = spark.sparkContext

    df = spark.read.csv('file:///D:/Products/AI/src/python-tutorials/spark_demos/spark_sql/test_data/people.csv',
                        sep=';', header=True)

    # Process duplicate rows
    df.dropDuplicates().show()
    df.dropDuplicates(['job', 'age']).show()

    # Process empty value rows
    df.dropna().show()
    # At least have 3 valid columns
    df.dropna(thresh=3, subset=['name', 'age']).show()

    # Fill empty data
    df.fillna('loss').show()
    df.fillna('N/A', subset=['job']).show()
    df.fillna({'name':'Unknown', 'age': 1, 'job': 'worker'}).show()