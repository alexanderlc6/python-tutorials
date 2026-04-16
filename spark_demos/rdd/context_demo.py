# coding: utf-8
from pyspark import SparkContext, SparkConf

def add(data):
    return data * 10

if __name__ == '__main__':
    conf = SparkConf().setAppName('word_count_demo')    # .setMaster("local[*]").
    sc = SparkContext(conf=conf)

    # Calculate word count from file in HDFS
    # file_rdd = sc.textFile('data/input/words.txt')
    file_rdd = sc.textFile('hdfs://localhost:9000/user/alexlc/data/input/words.txt')
    print('Default partition number', file_rdd.getNumPartitions())
    # batch_files_rdd = sc.wholeTextFiles('data/input/tiny_files')
    # print(batch_files_rdd.map(lambda x:x[1]).collect())

    # Split file
    words_rdd = file_rdd.flatMap(lambda line : line.split(' '))
    words_with_one_rdd = words_rdd.map(lambda x : (x, 1))
    # or use: words_with_one_rdd = words_rdd.map(add)
    # print(words_with_one_rdd.collect())

    # Group by key, then reduce for value list
    result_rdd = words_with_one_rdd.reduceByKey(lambda a, b : a + b)

    # Collect RDD data
    print(result_rdd.collect())

    rdd1 = sc.parallelize(['hap spk flink', 'spk spk hap', 'hap flink spk'])
    rdd2 = rdd1.flatMap(lambda x: x.split(' '))
    print(rdd2.collect())

    rdd3 = sc.parallelize([('a', 1), ('b', 2),('c', 1), ('a', 3), ('c', 1)])
    print(rdd3.reduceByKey(lambda a, b: a + b).collect())

    print(rdd3.map(lambda x:(x[0], x[1] * 10)).collect())
    print(rdd3.mapValues(lambda x: x * 10).collect())
    print('rdd3.groupBy:', rdd3.groupBy(lambda t : t[0]).map(lambda t : (t[0], list(t[1]))).collect())

    # Filter
    rdd4 = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(rdd4.filter(lambda x: x % 2 == 0).collect())

    # Remove duplicate elements
    rdd5 = sc.parallelize([1, 2, 3, 1, 1, 4, 3])
    print(rdd5.distinct().collect())
    print(rdd4.intersection(rdd5).collect())

    rdd5 = sc.parallelize([('a', 1),('a', 1),('a', 3)])
    print(rdd5.distinct().collect())

    # Union
    rdd6 = rdd4.union(rdd5)
    print(rdd6.collect())

    # Join(by key)
    rdd1 = sc.parallelize([(1001,'Zhangsan'), (1002,'Lisi'), (1003,'Wangwu'), (1004,'Caiwe')])
    rdd2 = sc.parallelize([(1001, 'AA'), (1002, 'BB'), (1003, 'CC')])
    print(rdd1.join(rdd2).collect())
    print(rdd1.leftOuterJoin(rdd2).collect())
    print(rdd1.rightOuterJoin(rdd2).collect())

    # Intersection
    rdd1 = sc.parallelize([('a', 1), ('a', 3)])
    rdd2 = sc.parallelize([('a', 1), ('b', 3)])
    print(rdd1.intersection(rdd2).collect())

    # rdd4 = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9], 3)
    rdd4 = sc.parallelize(range(1,10), 3)
    print(rdd4.glom().flatMap(lambda x:x).collect())
    print(rdd4.reduce(lambda a, b : a + b))
    print(rdd4.fold(10, lambda a, b : a + b))
    print(rdd4.first())
    print(rdd4.take(5))
    print(rdd4.top(3))
    print(rdd4.count())

    rdd1 = sc.parallelize([('a', 1), ('f', 5), ('e', 2), ('a', 1), ('b', 1), ('b', 3), ('b', 2), ('a', 6)])
    rdd2 = rdd1.groupByKey()
    print(rdd2.collect())
    print('rdd1.groupByKey:', rdd2.map(lambda x: (x[0], list(x[1]))).collect())
    print(rdd1.sortBy(lambda x: x[1], ascending=True, numPartitions=3).collect())
    print(rdd1.sortBy(lambda x: x[0], ascending=False, numPartitions=1).collect())

    rdd3 = sc.parallelize([('a', 1), ('F', 5), ('C', 2), ('d', 1), ('E', 3), ('b', 1), ('b', 3), ('e', 2), ('t', 1)])
    print(rdd3.sortByKey(ascending=True, numPartitions=1, keyfunc=lambda key: str(key).lower()).collect())

    # Count
    rdd1 = sc.textFile('file:///Users/alexlc/Products/src/AI/python-tutorials/spark_demos/data/input/words.txt')
    rdd2 = rdd1.flatMap(lambda x:x.split(' ')).map(lambda x:(x,1))
    print(rdd2.countByKey())
    # defaultdict(<class 'int'>, {'hello': 3, 'spark': 1, 'hadoop': 1, 'flink': 1})

    # Task sample randomly
    rdd1 = sc.parallelize([1,3,4,2,6,4,7,9], 3)
    print(rdd1.takeSample(True, 22))
    print(rdd1.takeSample(False, 5, 1))
    print(rdd1.takeOrdered(3))
    print(rdd1.takeOrdered(3, lambda x:-x))
    # Do by executor, not by driver
    rdd1.foreach(lambda x: print(x * 10))
    # rdd1.saveAsTextFile('file:///Users/alexlc/Products/src/AI/python-tutorials/spark_demos/data/output/save_text_file')
    rdd1.saveAsTextFile('hdfs://localhost:9000/user/alexlc/data/output/save_text_file')