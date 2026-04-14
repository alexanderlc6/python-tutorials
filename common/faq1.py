import dataclasses
from datetime import date

import pandas as pd
import numpy as np
import re

from pydantic import BaseModel

df = pd.read_json('ques1.json')
print(df)

# df.filter(regex='^[<\s>][/?!]\w+$').to_csv('newData1.csv')

from pyspark import SparkContext

spark = SparkContext(appName='test', master='local[*]', conf=None)


df['abstract'].replace('[<\w></\w>]', '', regex=True)
# df['abstract'].map(lambda x: re.sub('[^a-zA-Z0-9]', '', x)).filter(lambda x: x != '').collect()
print(df['abstract'].tolist())

with open('ques1.txt', 'w') as f:
    f.write('\n'.join(df['abstract'].tolist()))
rdd = spark.textFile('ques1.txt')

for tt in (rdd.map(lambda word:(word, 1))
        .groupBy(lambda word: word)
        .reduceByKey(lambda a,b:a+b).collect()):
    print(tt)

from pydantic import BaseModel
from dataclasses import dataclass

@dataclass
class ProcessorInfo(BaseModel):
    id: int
    title: str
    abstract: str
    publish_date: date

    def process(self):
        df = pd.read_json('ques1.json')
        print(df)

        df.filter(regex='^[<?>][/?!]\w+$').to_csv('newData1.csv')

        from pyspark import SparkContext

        spark = SparkContext(appName='test', master='local[*]', conf=None)
        print(df['abstract'].tolist())
        with open('ques1.txt', 'w') as f:
            f.write('\n'.join(df['abstract'].tolist()))
        rdd = spark.textFile('ques1.txt')

        abt_list = list()
        for tt in rdd.flatMap(lambda line: line.split(' ')).map(lambda word:(word, 1)).reduceByKey(lambda a,b:a+b).collect():
            print(tt)
            abt_list.append(tt)

        df.drop(axis=0, columns=['abstract'])
        df['new_abstract'] = abt_list

        kwd_info = KeywordInfo('abc', 23)
        # result_info = ResultInfo(kwd_info)
        result_info = self.__deepcopy__()
        result_info.__setattr__('keyword_info', kwd_info)
        result_info.__setattr__('vectorization_text', 'test')
        print(result_info)

@dataclass
class KeywordInfo():
    word: str
    frequency: int

@dataclass
class ResultInfo(KeywordInfo):
    id: int
    title: str
    publish_date: date
    new_abstract: str
    vectorization_text: str

if  __name__ == '__main__':
    df = pd.read_json('ques1.json')
    ProcessorInfo().process()

