import time

from pyspark import SparkContext, SparkConf, StorageLevel

if __name__ == '__main__':
    conf = SparkConf().setAppName('parel_demo').setMaster('local[*]')
    sc = SparkContext(conf=conf)

    rdd = sc.parallelize([1,2,3,4,5])
    print('Default partition number', rdd.getNumPartitions())

    rdd = sc.parallelize([1,2,3,4,5], 3)
    print('rdd content:', rdd.collect())

    rdd1 = sc.parallelize([1, 3, 4, 2, 6, 4, 7, 9], 3)
    def process(iter):
        result = list()
        for it in iter:
            result.append(it * 10)
        return result

    print(rdd1.mapPartitions(process).collect())

    rdd1 = sc.parallelize([1, 3, 4, 2, 6, 4, 7, 9], 3)
    def process(iter):
        result = list()
        for it in iter:
            result.append(it * 10)

    rdd1.foreachPartition(process)

    rdd2 = sc.parallelize([('a', 1), ('f', 5), ('e', 2), ('a', 1), ('b', 1), ('b', 3), ('b', 2), ('a', 6)])
    # Define partition
    def process(k):
        if 'a' == k or 'b' == k:
            return 0
        if 'e' == k:
            return 1

        return 2

    print(rdd2.partitionBy(3, process).glom().collect())

    # Modify partition
    print(rdd1.repartition(1).getNumPartitions())
    print(rdd1.repartition(3).getNumPartitions())

    print(rdd1.coalesce(1).getNumPartitions())
    print(rdd1.coalesce(5, shuffle=True).getNumPartitions())

    sc.setCheckpointDir('hdfs://localhost:9000/user/alexlc/data/output/checkpoint')
    rdd1 = sc.textFile('file:///Users/alexlc/Products/src/AI/python-tutorials/spark_demos/data/input/words.txt')
    rdd2 = rdd1.flatMap(lambda t: t.split(' '))
    rdd3 = rdd2.map(lambda x: (x, 1))
    # rdd3.cache()
    # rdd3.unpersist()
    rdd3.checkpoint()

    rdd3.persist(StorageLevel.MEMORY_AND_DISK_2)

    rdd4= rdd3.reduceByKey(lambda a, b : a+b)
    rdd5 = rdd3.groupByKey()
    rdd6 = rdd5.mapValues(lambda x:sum(x))
    print(rdd6.collect())

    # rdd3.unpersist()
    time.sleep(10000)
