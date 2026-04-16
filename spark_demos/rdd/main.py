import sys

import jieba
from pyspark import SparkConf, SparkContext, StorageLevel
# from def_search import content_jieba
import os
from operator import add

from spark_demos.rdd.def_search import content_jieba, filter_words, append_word, extract_user_and_word

python_path = sys.executable

# 设置 Driver 和 Executor 使用相同的 Python
os.environ['PYSPARK_PYTHON'] = python_path
os.environ['PYSPARK_DRIVER_PYTHON'] = python_path

if __name__ == '__main__':
    conf = SparkConf().setAppName('search_demo').setMaster('local[*]')
    sc = SparkContext(conf=conf)

    file_rdd = sc.textFile('file:///Users/alexlc/Products/src/AI/python-tutorials/spark_demos/data/input/SogouQ.txt')
    split_rdd = file_rdd.map(lambda x:x.split('\t'))
    split_rdd.persist(StorageLevel.DISK_ONLY)

    print(split_rdd.takeSample(True, 3))
    content_rdd = split_rdd.map(lambda x : x[2])
    words_rdd = content_rdd.flatMap(content_jieba)
    print(words_rdd.collect())
    filtered_rdd = words_rdd.filter(filter_words)
    final_words_rdd =  filtered_rdd.map(append_word)
    result = final_words_rdd.reduceByKey(lambda a, b : a+b).sortBy(lambda x:x[1], ascending=False, numPartitions=1).take(5)
    print('Requirement1 result:', result)

    # Requirement2：user and keyword composite analysis
    user_content_rdd = split_rdd.map(lambda x: (x[1], x[2]))
    print(user_content_rdd.collect())
    # Split words
    user_content_rdd.flatMap(lambda x: x[1].split(' '))
    user_word_with_one_rdd = user_content_rdd.flatMap(extract_user_and_word)
    result2 = user_word_with_one_rdd.reduceByKey(lambda a, b : a+b).sortBy(lambda x:x[1], ascending=False, numPartitions=1).take(5)
    print('Requirement2 result:', result2)

    # Time scope analysis
    time_rdd = split_rdd.map(lambda x: x[0])
    hour_with_one_rdd = time_rdd.map(lambda x: (x.split(':')[0], 1))
    result3 = hour_with_one_rdd.reduceByKey(add).sortBy(lambda x : x[1], ascending=False, numPartitions=1).collect()
    print('Requirement3 result:', result3)
