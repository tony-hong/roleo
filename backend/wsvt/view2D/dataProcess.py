'''
    This module provide query processing for the 
    rv.structure.Tensor object which are stored in hdf5 format.

    @Author: 
        Tony Hong

    @Environment:
        Already implemented in this file, so no need to export again
        These paths are only for reference 

        export LD_LIBRARY_PATH=hdf5/1.8.16/lib
        export PYTHONPATH=$PYTHONPATH:Rollenverteilung/src/lib
        export PYTHONPATH=$PYTHONPATH:view2D
'''

import os
import math
import sys

# Configuration of environment
sys.path.append('Rollenverteilung/src/lib')
os.system('export LD_LIBRARY_PATH=hdf5/1.8.16/lib')

import matplotlib.pyplot as plt
import pandas as pd

from rv.structure.Tensor import Matricisation
from rv.similarity.Similarity import cosine_sim

import view2D.errorCode as errorCode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

wordVectors = dict()
simularities = dict()
wordSupports = dict()
fractions = dict()
result = dict()

# ISSUE can be controlled form the front end
power = 10

matrix = Matricisation({
    'word0' : os.path.join(BASE_DIR, 'wackylmi-malt-v2-36K.word0.h5'),
    'word1' : os.path.join(BASE_DIR, 'wackylmi-malt-v2-36K.word1.h5') 
})


'''
    Processing function for the query for the client

    @parameters: 
        verb : str
        noun : str
        role : str 
        group : str
        topN   : int  # Number of top vectors which will be returned

    @return: result = dict()
'''
def process(verb, noun, role, group, topN = 20):
    print 'process start...' 
    memberIndex = dict()
    result = dict()
    double = False

    # query word 0 # with '-v/-n' suffix
    query0 = ''
    # query word 1 # with '-v/-n' suffix
    query1 = ''
    # with '-1' suffix if noun selects noun
    semanticRole = ''

    # Case of noun selects verb
    if group == 'noun':
        query0 = noun + '-n'
        semanticRole = role + '-1'
        if verb:
            double = True
            query1 = verb + '-v'
    # Case of verb selects noun
    elif group == 'verb':
        query0 = verb + '-v'
        semanticRole = role
        if noun:
            double = True
            query1 = noun + '-n'
    else:
        print 'exception: internal error!'
        result = {'errCode' : errorCode.INTERNAL_ERROR}
        return result

    # LOG
    print 'query0: ' + query0
    print 'query1: ' + query1
    print 'semanticRole: ' + semanticRole
    print 'double: ' + str(double)
    print 'topN: ' + str(topN)

    # members[0]: vectors
    # members[1]: list of words
    memberTuple = matrix.getMemberVectors(query0, 'word1', 'word0', {'link':[semanticRole]}, topN)

    if type(memberTuple) != type(tuple()):
        print 'exception: memberVectors is empty' 
        result = {'errCode' : errorCode.MBR_VEC_EMPTY}
        return result
    else:
        vectorList, wordList = memberTuple

    wordVectors = dict(zip(wordList, vectorList))

    print 'getMemberVectors finished...'
    print wordList

    resultList = []
    queryFraction = 0
    queryCosine = 0
    maxmaxSupport = 0

    # ISSUE: double call of getMemberVectors, need improvement
    # centroid = matrix.getCentroid(query0, 'word1', 'word0', {'link':[semanticRole]})
    centroid = pd.concat(vectorList).sum(level=[0,1])

    for w in wordList:
        v = wordVectors[w]

        support = v.ix[semanticRole].ix[query0]
        wordSupports[w] = support

        if support > maxmaxSupport:
            maxmaxSupport = support

    if double:
        # process query
        query = matrix.getRow('word0', query1)

        print 'getting query finished'

        if query.isnull().all():
            print 'exception: query is empty'
            result = {'errCode' : errorCode.QUERY_EMPTY}
            return result
        try:
            vector = query.ix[semanticRole]
            if vector.get(query0, 0) == 0:
                queryCosine = cosine_sim(centroid, query)
                print 'exception: query.ix[semanticRole].ix[query0] is empty'
            else:
                support = vector.ix[query0] 
                queryFraction = float(support) / maxmaxSupport
                queryCosine = cosine_sim(centroid, query)
        except KeyError:
            print 'exception: query.ix[semanticRole] is empty'
            result = {'errCode' : errorCode.SMT_ROLE_EMPTY}
            return result

        # Apply mapping to query
        q_x, q_y = mapping(queryFraction, queryCosine)
        if query1 in wordList:
            wordList.remove(query1)

    for w in wordList:
        fraction = float(wordSupports[w]) / maxmaxSupport

        wordCosine = cosine_sim(centroid, wordVectors[w])

        # Apply mapping to each word
        x, y = mapping(fraction, wordCosine)

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



'''
    Mapping from fraction, and cosine to the x, y coordinate

    @parameters:
        fraction = support / maxmaxSupport
        cosine   = cosine_sim(centroid, wordVector)
    @return: (x, y) = tuple
'''
def mapping(fraction, cosine):
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
