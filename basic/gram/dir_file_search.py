import os
import shutil

def search_dir(path, result):
    child_files = os.listdir(path)
    for child in child_files:
        child = os.path.join(path, child)

        result.append(child)
        if(os.path.isdir(child)):
            search_dir(child, result)

input_dir = input("Input dir to search:")
output_dir = input("Input dir to save:")

files = list()
search_dir(input_dir, files)

for file in files:
    print('find %s'%(file))

    if os.path.isfile(file) and file.endswith('.txt'):
        print('move %s'%(file))
        shutil.move(file, output_dir)