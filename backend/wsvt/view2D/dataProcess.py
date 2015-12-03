'''
@Author: 
    Tony Hong
@Environment:
    export LD_LIBRARY_PATH=~/ROOT/wsvt/workspace/wsvt/hdf5/1.8.16/lib/
    export PYTHONPATH=$PYTHONPATH:~/ROOT/wsvt/workspace/wsvt/Rollenverteilung/src/lib
    export PYTHONPATH=$PYTHONPATH:~/ROOT/wsvt/workspace/wsvt/view2D/

    for 
        ~/ROOT/wsvt/workspace/
    need to be modified to the real absolute path of the project folder
    (base directory of git repository)
'''

import os
import math

import matplotlib.pyplot as plt
import pandas as pd

from rv.structure.Tensor import Matricisation
from rv.similarity.Similarity import cosine_sim

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

topWords = dict()
simularities = dict()
counts = dict()
fractions = dict()
power = 10
matrix = Matricisation({
    'word0' : os.path.join(BASE_DIR, 'wackylmi-malt-v2-36K.word0.h5'),
    'word1' : os.path.join(BASE_DIR, 'wackylmi-malt-v2-36K.word1.h5') 
})
# class BusinessLogic(object):
#     """docstring for BusinessLogic"""
#     def __init__(self):
#         super(BusinessLogic, self).__init__()

    
def process(verb='eat-v', semanticRole='A0', queryWord='apple'):
    print 'process start...'
    # members[0]: vectors
    # members[1]: list of words
    memberVectors, wordList = matrix.getMemberVectors(verb, 'word1', 'word0', {'link':[semanticRole]})

    print 'getMemberVectors finished...'
    print wordList

    resultList = []

    # ISSUE: double call of getMemberVectors, need improvement
    # centroid = matrix.getCentroid(verb, 'word1', 'word0', {'link':[semanticRole]})
    centroid = pd.concat(memberVectors).sum(level=[0,1])
    countOfCentroid = centroid.ix[semanticRole].ix[verb]

    for w in wordList:
        row = matrix.getRow('word0', w)
        topWords[w] = row
        wordCosine = cosine_sim(centroid, row)

        if row.ix[semanticRole].get(verb, 0) == 0:
            count = 0
        else:
            count = row.ix[semanticRole].ix[verb]

        fraction = float(count) / countOfCentroid

        rad = math.acos(wordCosine) * 4
        r = pow((1 - fraction), power)
        x = r * math.cos(rad)
        y = r * math.sin(rad)

        simularities[w] = wordCosine
        counts[w] = count        
        fractions[w] = fraction

        resultList.append({
            'y'     : y,
            'x'     : x, 
            'cos'   : wordCosine, 
            'word'  : w,

        })

    print 'result list is prepared'

    # process query
    query = matrix.getRow('word0', queryWord)
    queryCosine = cosine_sim(centroid, query)

    if query.ix[semanticRole].get(verb, 0) == 0:
        queryFraction = 0
    else:
        # ISSUE: add the self-count to the denominator
        queryFraction = query.ix[semanticRole].ix[verb] / (countOfCentroid + query.ix[semanticRole].ix[verb])
        # queryFraction = query.ix[semanticRole].ix[verb] / (countOfCentroid )

    q_r = pow((1 - queryFraction), power)
    q_rad = math.acos(queryCosine) * 4
    q_x = q_r * math.cos(q_rad)
    q_y = q_r * math.sin(q_rad)

    result = {
        'queried' : 
        {
            'y'    : q_y,
            'x'    : q_x,
            'cos'  : queryCosine,
            'word' : queryWord,
        }, 
        'nodes' : resultList
    }

    print 'result creating is prepared'

    return result

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

def printCoordinates():
    X = []
    Y = []
    for w in wordList:
        sub = 20
        s = str.ljust(w, sub)
        rad = math.acos(simularities[w]) * 4
        r = pow((1 - fractions[w]), power)
        x = r * math.cos(rad)
        y = r * math.sin(rad)
        X.append(x)
        Y.append(y)
        print 'word: %s x:\t %f \t y:\t %f \t r:\t %f \t rad:\t %f' % (s, x, y, r, rad)

    print X
    print Y
    print 'queryWord: \t' + queryWord + '\t cosine_sim: \t' + str(queryCosine) + '\tx: \t' + str(q_x) + '\ty: \t' + str(q_y)


def plotG():
    plt.plot(0, 0, 'ro')
    plt.plot(X, Y, 'bo')
    plt.plot(q_x, q_y, 'go')
    plt.savefig('fig.png')
    plt.show
