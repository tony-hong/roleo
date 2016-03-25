'''
    This module provide query processing for the rv.structure.Tensor object 
    which are stored in hdf5 format.

    @Author: 
        Tony Hong

    @Environment:
        Already implemented in this file, so no need to export again.
        These paths are only for reference 

        export LD_LIBRARY_PATH=hdf5/1.8.16/lib
        export PYTHONPATH=$PYTHONPATH:Rollenverteilung/src/lib
        export PYTHONPATH=$PYTHONPATH:view2D
'''

import os
import math
import sys
import logging

# Configuration of environment
sys.path.append('Rollenverteilung/src/lib')
os.system('export LD_LIBRARY_PATH=hdf5/1.8.16/lib')

import pandas as pd

from rv.structure.Tensor import Matricisation
from rv.similarity.Similarity import cosine_sim

import view2D.errorCode as errorCode

logger = logging.getLogger('django')

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

wordVectors = dict()
simularities = dict()
wordSupports = dict()
fractions = dict()
result = dict()

# Initialize data structure Matricisation
matrix = Matricisation({
    'word0' : os.path.join(BASE_DIR, 'wackylmi-malt-v2-36K.word0.h5'),
    'word1' : os.path.join(BASE_DIR, 'wackylmi-malt-v2-36K.word1.h5') 
})


def process(verb, noun, role, group, topN = 20):
    '''
    Processing function for the query for the client

    @parameters: 
        verb    : str  # without suffix
        noun    : str  # without suffix
        role    : str  # semantic role without suffix
        group   : str  # string in the set {'verb', 'noun'} indicating the primal query word
        topN    : int  # number of top vectors which will be returned

    @return: result = dict()

    ''' 
    logger.info('process start...')

    memberIndex = dict()
    result = dict()
    double = False

    # primal query word # with '-v/-n' suffix
    query0 = ''
    # second query word # with '-v/-n' suffix
    query1 = ''
    # with '-1' suffix if noun selects noun
    semanticRole = ''

    # Adding suffix according to different types of query
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
        logger.critical( 'errCode: %d. internal error!', errorCode.INTERNAL_ERROR)
        result = {'errCode' : errorCode.INTERNAL_ERROR}
        return result

    # LOG
    logger.debug('query0: %s' , query0)
    logger.debug('query1: %s' , query1)
    logger.debug('semanticRole: %s' , semanticRole)
    logger.debug('group: %s' , group)
    logger.debug('top_results: %d' , topN)

    # memberTuple[0]: list of vectors
    # memberTuple[1]: list of words
    memberTuple = matrix.getMemberVectors(query0, 'word1', 'word0', {'link':[semanticRole]}, topN)

    # A hack checking whether the return is empty
    # if it is not tuple(), it is empty, the model return nothing for the primal query word
    if type(memberTuple) != type(tuple()):
        logger.error('errCode: %d. memberVectors is empty', errorCode.MBR_VEC_EMPTY)
        result = {'errCode' : errorCode.MBR_VEC_EMPTY}
        return result
    else:
        vectorList, wordList = memberTuple

    # Reshape wordList, vectorList to a dict(), with key is word and value is vector
    wordVectors = dict(zip(wordList, vectorList))
  
    # LOG
    logger.info('getMemberVectors finished...')
    # print wordList

    resultList = []
    queryFraction = 0
    queryCosine = 0
    maxSupport = 0

    # Compute centroid from the vectorList using pandas
    centroid = pd.concat(vectorList).sum(level=[0,1])

    # Obtain all supports and compute the max support 
    for w in wordList:
        v = wordVectors[w]

        support = v.ix[semanticRole].ix[query0]
        wordSupports[w] = support

        if support > maxSupport:
            maxSupport = support

    # if there are 2 query words, process the second query word
    if double:
        # process query
        query = matrix.getRow('word0', query1)

        logger.info('getting query finished')

        if query.isnull().all():
            # Second query word does not exist in the model
            logger.error( 'errCode: %d. query is empty', errorCode.QUERY_EMPTY)
            result = {'errCode' : errorCode.QUERY_EMPTY}
            return result
        try:
            vector = query.ix[semanticRole]
            if vector.get(query0, 0) == 0:
                # For the second query word, in this semantic role, the primal query word does not exist
                queryCosine = cosine_sim(centroid, query)
                logger.info('query.ix[semanticRole].ix[query0] is empty')
            else:
                support = vector.ix[query0] 

                # Computer fraction and cosine
                # If the mapping function is changed, this must be changed
                queryFraction = float(support) / maxSupport
                queryCosine = cosine_sim(centroid, query)
        except KeyError:
            # Semantic role of second query word does not exist
            logger.error( 'errCode: %d. query.ix[semanticRole] is empty', errorCode.SMT_ROLE_EMPTY)
            result = {'errCode' : errorCode.SMT_ROLE_EMPTY}
            return result

        # Apply mapping to second query word
        q_x, q_y = mapping(queryFraction, queryCosine)
        if query1 in wordList:
            wordList.remove(query1)

    # Computer fraction and cosine
    # If the mapping function is changed, this must be changed
    for w in wordList:
        fraction = float(wordSupports[w]) / maxSupport

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

    logger.info('result list is prepared')

    result = {
        'nodes' : resultList
    }

    # if there are 2 query words
    if double:
        result['queried'] = {
                'y'    : q_y,
                'x'    : q_x,
                'cos'  : queryCosine,
                'word' : query1,
            }

    logger.info('result creating is prepared')

    return result



def mapping(fraction, cosine):
    '''
    Mapping from fraction, and cosine to the x, y coordinate.
    This is a simple function which maps the high dimension vector to 2D.
    It is suitable for a web tool which need a short response time.

    @parameters:
        fraction = support / maxSupport
        cosine   = cosine_sim(centroid, wordVector)
    @return: 
        (x, y) is a tuple
    '''
    # Scale fraciton and cosine, let them become more sparse over [0, 1]
    y = math.pow(fraction, 0.4)
    x = math.pow(cosine, 0.8)

    # Compute radial coordinates
    r = math.sqrt((math.pow(1-x, 2) + math.pow(1-y, 2)) / 2)
    if x == 0:
        rad = math.pi / 2
    else:
        # Scale rad from [0, pi/2] to [0, 2 * pi]
        rad = math.atan(y / x) * 4

    # Transform back to Cartesian coordinates
    x = r * math.cos(rad)
    y = r * math.sin(rad)

    return x, y
