import jieba

if __name__ == '__main__':
    content = '小明硕士毕业于中国科学院计算所,后在清华大学深造'
    result = jieba.cut(content, cut_all=True)
    print(list(result))
    print(type(result))

    result = jieba.cut(content, False)
    print(list(result))

    # Search engine mode
    result3 = jieba.cut_for_search(content)
    print(','.join(result3))