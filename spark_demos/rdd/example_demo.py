from pyspark import SparkConf, SparkContext
import json
# import os
from def_funcs import city_with_category

# os.environ['HADOOP_CONF_DIR'] = '/opt/homebrew/opt/hadoop/libexec/etc/hadoop'

if __name__ == '__main__':
    # conf = SparkConf().setAppName('example_demo').setMaster('local[*]')
    conf = SparkConf().setAppName('test-yarn-1').setMaster('yarn')
    conf.set('spark.submit.pyFiles', 'def_funcs.py')
    sc = SparkContext(conf=conf)
    # file_rdd = sc.textFile('file:///Users/alexlc/Products/src/AI/python-tutorials/spark_demos/data/input/order.text')
    file_rdd = sc.textFile('hdfs://localhost:9000/user/alexlc/data/input/order.text')

    # Split by [|]
    jsons_rdd = file_rdd.flatMap(lambda t: t.split('|'))
    dict_rdd = jsons_rdd.map(lambda json_str : json.loads(json_str))
    print(dict_rdd.collect())

    bj_rdd = dict_rdd.filter(lambda t : t['areaName'] == '北京')
    category_rdd = bj_rdd.map(city_with_category)

    print(category_rdd.distinct().collect())