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


def process(verb, noun, semanticRole, group):
    print 'process start...'

    double = False
    if group == 'noun':
        if noun:
            query0 = noun + '-n'
            semanticRole = semanticRole + '-1'
            if verb:
                query1 = verb + '-v'
                double = True
        else:
            # EXCEPTION
            print 'case: noun is empty'
    elif group == 'verb':
        if verb:
            query0 = verb + '-v'
            if noun:
                query1 = noun + '-n'
                double = True
        else:
            # EXCEPTION
            print 'case: verb is empty'
    else:
        print 'internal error!'

    # members[0]: vectors
    # members[1]: list of words
    memberVectors, wordList = matrix.getMemberVectors(query0, 'word1', 'word0', {'link':[semanticRole]})

    print 'getMemberVectors finished...'
    print wordList

    resultList = []
    queryFraction = 0
    queryCosine = -1

    # ISSUE: double call of getMemberVectors, need improvement
    # centroid = matrix.getCentroid(query0, 'word1', 'word0', {'link':[semanticRole]})
    centroid = pd.concat(memberVectors).sum(level=[0,1])
    # TODO
    countOfCentroid = centroid.ix[semanticRole].ix[query0]

    if double:
        # process query
        query = matrix.getRow('word0', query1)

        print 'getting query finished'

        if query.isnull().all():
            # TODO: raise exception
            print 'case: query is empty'
        elif query.ix[semanticRole].get(query0, 0) == 0:
            # TODO: raise exception
            print 'case: query.ix[semanticRole].ix[query0] is empty'
        else:
            # ISSUE: add the self-count to the denominator
            queryFraction = query.ix[semanticRole].ix[query0] / (countOfCentroid + query.ix[semanticRole].ix[query0])
            # queryFraction = query.ix[semanticRole].ix[query0] / (countOfCentroid )
            queryCosine = cosine_sim(centroid, query)

        q_r = pow((1 - queryFraction), power)
        q_rad = math.acos(queryCosine) * 4
        q_x = q_r * math.cos(q_rad)
        q_y = q_r * math.sin(q_rad)


    for w in wordList:
        if double and w == query1:
            continue
        row = matrix.getRow('word0', w)
        topWords[w] = row
        wordCosine = cosine_sim(centroid, row)

        count = row.ix[semanticRole].ix[query0]

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

    if double:
        result = {
            'queried' : 
            {
                'y'    : q_y,
                'x'    : q_x,
                'cos'  : queryCosine,
                'word' : query1,
            }, 
            'nodes' : resultList
        }
    else:
        result = {
            'queried' : '', 
            'nodes' : resultList
        }

    print 'result creating is prepared'

    return result


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
    print 'query1: \t' + query1 + '\t cosine_sim: \t' + str(queryCosine) + '\tx: \t' + str(q_x) + '\ty: \t' + str(q_y)

def plotG():
    plt.plot(0, 0, 'ro')
    plt.plot(X, Y, 'bo')
    plt.plot(q_x, q_y, 'go')
    plt.savefig('fig.png')
    plt.show
