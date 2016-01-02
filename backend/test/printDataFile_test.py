import os
import pickle, pprint

vectorDir = 'sharevectors'
fileList = os.listdir(vectorDir)
fileIndex = dict()
dataIndex = dict()

print 'File list is: '
for i in range(len(fileList)):
    fileIndex[i] = fileList[i]
    print str(i) + ': ' + fileList[i]
print '\n'

print 'Obtaining data list...'
for key, val in fileIndex.items():
    f = open(vectorDir + '/' + val, 'rb')
    dataIndex[val] = pickle.load(f)
    print 'ID: ' + str(key) + '\t File name: ' + val
print '\n'

def printAll():
    for key, val in dataIndex.items():
        print 'Data for file ' + key
        pprint.pprint(val)
        print '\n'

printAll()