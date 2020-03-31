import time
from lxml import etree
from xmldiff import main, formatting
from zipfile import ZipFile
import re

path = input('Please enter file path: ')
test = 1
#diff = main.diff_files(path1, path2,
#                       formatter=formatting.XMLFormatter(pretty_print=True))

def waitforinput():
    global test
    action = input('What do you want to do? ')
    if action=='path':
        path = input('Please enter file path: ')
    elif action=='compare':
        comparedocs()
    elif action=='scan':
        test = scandoc(test)

def scandoc(iteration):
    with ZipFile(path, 'r') as f:
        if iteration == 1:
            f.extractall('extractedpptx1')
            iteration=2
        else:
            f.extractall('extractedpptx2')
            iteration=1
    return iteration

def comparedocs():
    path1 = 'extractedpptx1/ppt/slideMasters/slideMaster1.xml'
    path2 = 'extractedpptx2/ppt/slideMasters/slideMaster1.xml'
    diff = main.diff_files(path1, path2, formatter=formatting.XMLFormatter(pretty_print=True))
    differences = [m.start() for m in re.finditer('diff:', diff)]
    print('---------------\n' + diff + '\n----------------')
    print('Differences found at positions: ' + str(differences))

# with open('differences.txt', 'w+') as f:
#     msg = '-'*30 + '\n'
#     msg += 'DIFFERENCES between [' + path + '] and [' + path2 + ']:\n'
#     msg += diff
#     msg += '-'*30
#     f.write(msg)
#     print('Sucessfully wrote to txt!')
#     print(msg)

while True:
    waitforinput()