f = open('test.txt', 'w+')
f.write('World')
print('Create test file and write in.')

f = open('test.txt', 'r+')
f.write('Hello')
print('Open test file and override content.')

f = open('test.txt', 'a')
f.write(' ==append== ')
print('Create test file and write in.')

f_name = '/Users/alexlc/Products/src/AI/python-tutorials/basic/gram/test.txt'
f = open(f_name, 'a+')
f.write('World')
print('Append at the end of file.')

f= None
try:
    f = open(f_name)
    content = f.read()
    print(content)
except FileNotFoundError as e:
    print('File not found: {}'.format(e))
except OSError as e:
    print('OS error: {}'.format(e))
finally:
    if f is not None:
        f.close()

# Auto collect resource
with open(f_name) as f:
    content = f.read()
    print(content)

# Read/Write text file demo
test_f_name = 'src_text.txt'
with open(test_f_name, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    copy_f_name = 'dest_file.txt'
    with open(copy_f_name, 'w', encoding='utf-8') as copy_f:
        copy_f.writelines(lines)
        print('Text file copy succeed!')

# Read/Write binary file demo
f_bn_name = '1.jpg'
with open(f_bn_name, 'rb') as f:
    b = f.read()
    copy_f_name = '1_copy.jpg'
    with open(copy_f_name, 'wb') as copy_f:
        copy_f.write(b)
        print('Binary file copy succeed!')