from pyspark import SparkConf, SparkContext
import re


if __name__ == '__main__':
    conf = SparkConf().setAppName('broadcast_demo').setMaster('local[*]')
    sc = SparkContext(conf=conf)

    stu_info_list = [(1, '张大仙', 11),
                     (2, '王晓晓', 13),
                     (3, '张甜甜', 11),
                     (4, '王大力', 11)]
    broadcast = sc.broadcast(stu_info_list)

    def map_func(data):
        id = data[0]
        name = ''
        for info in broadcast.value:
            if id == info[0]:
                name = info[1]

        return (name, data[1], data[2])

    score_info_rdd = sc.parallelize([
        (1, '语文', 99),
        (2, '数学', 99),
        (3, '英语', 99),
        (4, '编程', 99),
        (1, '语文', 99),
        (2, '编程', 99),
        (3, '语文', 99),
        (4, '英语', 99),
        (1, '语文', 99),
        (3, '英语', 99),
        (2, '编程', 99)
    ])

    print(score_info_rdd.map(map_func).collect())

    # Accumulate demo
    rdd = sc.parallelize([1,2,3,4,5,6,7,8,9,10], 2)
    # count = 0
    acumlt = sc.accumulator(0)

    def map_fun(data):
        # global count
        # count += 1
        # print(count)
        global acumlt
        acumlt += 1
        print(acumlt)

    rdd2 = rdd.map(map_fun)
    rdd2.cache()
    rdd2.collect()
    rdd3 = rdd2.map(lambda x:x).collect()

    # print(count)      # Output is 0 - Error!
    print(acumlt)


    # Example:
    file_rdd = sc.textFile('file:///Users/alexlc/Products/src/AI/python-tutorials/spark_demos/data/input/accumulator_broadcast_data.txt')
    abnormal_chars = [',', '.', '!', '#', '$', '%']
    broadcast_char = sc.broadcast(abnormal_chars)
    acmlt = sc.accumulator(0)
    line_rdd = file_rdd.filter(lambda x: x.strip()).map(lambda x:x.strip())

    # Split by blanks
    words_rdd = line_rdd.flatMap(lambda line : re.split('\s+', line))

    def filter_func(data):
        global acmlt
        abnormal_chars = broadcast_char.value
        if data in abnormal_chars:
            acmlt += 1
            return False
        else:
            return True


    normal_words_rdd = words_rdd.filter(filter_func)
    result_rdd = normal_words_rdd.map(lambda x: (x, 1)).reduceByKey(lambda a,b : a+b)
    print('Normal words:', result_rdd.collect())
    print('Abnormal char count:', acmlt)
    # Output:
    # Normal words: [('hadoop', 3), ('hive', 6), ('spark', 11), ('mapreduce', 4), ('sql', 2), ('hdfs', 2)]
    # Abnormal char count: 8