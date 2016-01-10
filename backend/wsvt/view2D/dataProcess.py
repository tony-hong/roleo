'''
@Author: 
    Tony Hong
@Environment:
    export LD_LIBRARY_PATH=hdf5/1.8.16/lib
    export PYTHONPATH=$PYTHONPATH:Rollenverteilung/src/lib
    export PYTHONPATH=$PYTHONPATH:view2D
    
'''

import os
import math

import matplotlib.pyplot as plt
import pandas as pd

from rv.structure.Tensor import Matricisation
from rv.similarity.Similarity import cosine_sim
import errorCode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

topWords = dict()
simularities = dict()
counts = dict()
fractions = dict()
result = dict()

# ISSUE can be controlled form the front end
power = 10

matrix = Matricisation({
    'word0' : os.path.join(BASE_DIR, 'wackylmi-malt-v2-36K.word0.h5'),
    'word1' : os.path.join(BASE_DIR, 'wackylmi-malt-v2-36K.word1.h5') 
})


def process(verb, noun, semanticRole, group):
    print 'process start...'

    double = False
    result = {}
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
            result['errCode'] = errorCode.NOUN_EMPTY
            return result
    elif group == 'verb':
        if verb:
            query0 = verb + '-v'
            if noun:
                query1 = noun + '-n'
                double = True
        else:
            # EXCEPTION
            print 'case: verb is empty'
            result['errCode'] = errorCode.VERB_EMPTY
            return result            
    else:
        print 'internal error!'
 
    # members[0]: vectors
    # members[1]: list of words
    memberVectors, wordList = matrix.getMemberVectors(query0, 'word1', 'word0', {'link':[semanticRole]}, 20)

    # if query.isnull().all():
    #     print 'verb is empty' 
    # else:
    #     memberVectors, wordList = temp

    print 'getMemberVectors finished...'
    print wordList

    resultList = []
    queryFraction = 0
    queryCosine = 0    
    maxCount = 0

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
            queryCosine = cosine_sim(centroid, query)
            # TODO: raise exception
            print 'case: query.ix[semanticRole].ix[query0] is empty'
        else:
            # ISSUE: add the self-count to the denominator
            count = query.ix[semanticRole].ix[query0] 
            queryFraction = float(count) / (countOfCentroid + count)
            # queryFraction = query.ix[semanticRole].ix[query0] / (countOfCentroid )
            queryCosine = cosine_sim(centroid, query)

        # TODO: Find a better mapping
        q_x, q_y = mapping2(queryFraction, queryCosine)

    for w in wordList:
        row = matrix.getRow('word0', w)
        topWords[w] = row

        count = row.ix[semanticRole].ix[query0]
        counts[w] = count

        if count > maxCount:
            maxCount = count

    for w in wordList:
        row = matrix.getRow('word0', w)
        fraction = float(counts[w]) / maxCount

        wordCosine = cosine_sim(centroid, row)
        # TODO: Find a better mapping
        x, y = mapping2(fraction, wordCosine)

        simularities[w] = wordCosine
        fractions[w] = fraction

        resultList.append({
            'y'     : y,
            'x'     : x, 
            'cos'   : wordCosine, 
            'word'  : w,

        })

    print 'result list is prepared'

    result = {
        'nodes' : resultList
    }
    if double:
        result['queried'] = {
                'y'    : q_y,
                'x'    : q_x,
                'cos'  : queryCosine,
                'word' : query1,
            }

    print 'result creating is prepared'

    return result


def mapping1(fraction, cosine):
    rad = math.acos(cosine) * 4
    r = pow((1 - fraction), power)
    x = r * math.cos(rad)
    y = r * math.sin(rad)    
    return x, y

def mapping2(fraction, cosine):
    y = math.pow(fraction, 0.4)
    x = math.pow(cosine, 0.8)
    r = math.sqrt((math.pow(1-x, 2) + math.pow(1-y, 2)) / 2)
    if x == 0:
        rad = math.pi / 2
    else:
        rad = math.atan(y / x) * 4
    x = r * math.cos(rad)
    y = r * math.sin(rad)
    return x, y

def mapping3(fraction, cosine):
    f = fraction * 2 * math.pi % math.pi
    r = math.pow(1 - cosine, 10)
    rad = f
    x = r * math.cos(rad)
    y = r * math.sin(rad)
    return x, y

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
