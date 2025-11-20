file1=open('../../resources/readTest.txt','r', 1, 'GBK')
file2=open('../../resources/writeTest.txt','w')
words = file1.read()

for w in words:
    if w >='a' and w <='z' or w >='A' and w <'Z':
        file2.write(w)

file1.close()
file2.close()

