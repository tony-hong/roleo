'''
@Author: 
    Tony Hong
@Environment:
    export LD_LIBRARY_PATH=/usr/local/Cellar/hdf5/1.8.16/lib/
    export PYTHONPATH=$PYTHONPATH:~/ROOT/wsvt/Rollenverteilung/src/lib/

'''
import pandas as pd
import os
import math
import matplotlib.pyplot as plt

from rv.structure.Tensor import Matricisation
from rv.similarity.Similarity import cosine_sim

semanticRole = 'A0'
verb = 'eat-v'
queryWord = 'teenager-n'

topWords = dict()
simularities = dict()
counts = dict()
fractions = dict()
fractionsSum = 0

X = []
Y = []

matrix = Matricisation({'word0':'wackylmi-malt-v2-36K.word0.h5', 'word1':'wackylmi-malt-v2-36K.word1.h5'})

# members[0]: vectors
# members[1]: list of words
memberVectors, wordList = matrix.getMemberVectors(verb, 'word1', 'word0', {'link':[semanticRole]})

# ISSUE: double call of getMemberVectors, need improvement
# centroid = matrix.getCentroid(verb, 'word1', 'word0', {'link':[semanticRole]})
centroid = pd.concat(memberVectors).sum(level=[0,1])
countOfCentroid = centroid.ix[semanticRole].ix[verb]


for w in wordList:
    row = matrix.getRow('word0', w)
    topWords[w] = row
    simularities[w] = cosine_sim(centroid, row)
    count = row.ix[semanticRole].ix[verb]
    counts[w] = count
    fraction = float(count) / countOfCentroid
    fractions[w] = fraction
    fractionsSum = fractionsSum + fraction

# def printSims_Counts():
#     for w in printingList:
#         sub = 20
#         s = str.ljust(w, sub)
#         print 'word: %s simularity:\t %f \t count:\t %d \t fraction:\t %f' % (s, simularities[w], counts[w], fractions[w])

# printSims_Counts()



# def printCoordinates():
#     for w in wordList:
#         sub = 20
#         s = str.ljust(w, sub)
#         x = (1 - simularities[w]) * 100
#         y = (1 - fractions[w]) * 100
#         r = math.sqrt(math.pow(x, 2) + math.pow(y, 2))
#         rad = math.atan(y / x) * 4 # / (2 * math.pi) * 360 # degree
#         x = r * math.cos(rad)
#         y = r * math.sin(rad)
#         X.append(x)
#         Y.append(y)
#         # print 'word: %s x:\t %f \t y:\t %f \t r:\t %f \t deg:\t %f' % (s, x, y, r, rad)

def printCoordinates(pw):
    for w in wordList:
        sub = 20
        s = str.ljust(w, sub)
        rad = math.acos(simularities[w]) * 4
        r = pow((1 - fractions[w]), pw)
        x = r * math.cos(rad)
        y = r * math.sin(rad)
        X.append(x)
        Y.append(y)
        print 'word: %s x:\t %f \t y:\t %f \t r:\t %f \t rad:\t %f' % (s, x, y, r, rad)

# process query
query = matrix.getRow('word0', queryWord)
querySim = cosine_sim(centroid, query)
queryFraction = query.ix[semanticRole].ix[verb] / (countOfCentroid + query.ix[semanticRole].ix[verb])
q_r = pow((1 - queryFraction), 10)
q_rad = math.acos(querySim) * 4
q_x = q_r * math.cos(q_rad)
q_y = q_r * math.sin(q_rad)

print 'sum of fractions: ' + str(fractionsSum)

printCoordinates(10)

print X
print Y
print 'queryWord: \t' + queryWord + '\t cosine_sim: \t' + str(querySim) + '\tx: \t' + str(q_x) + '\ty: \t' + str(q_y)

def plotG():
    plt.plot(0, 0, 'ro')
    plt.plot(X, Y, 'bo')
    plt.plot(q_x, q_y, 'go')
    plt.savefig('fig.png')
    plt.show

plotG()
