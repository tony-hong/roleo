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

import math
import logging

import numpy as np
import pandas as pd

from rv.similarity.Similarity import cosine_sim

import errorCode as errorCode
from matrixFactory import MatrixFactory
from roleDict import getRoleMapping

mf = MatrixFactory()
logger = logging.getLogger('django')


def process(verb, noun, role, group, model, topN = 20):
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
    matrix = mf.getMatrix()

    wordVectors = dict()
    wordSupports = dict()
    # simularities = dict()
    # fractions = dict()
    result = dict()
    
    logger.info('process start...')

    memberIndex = dict()
    double = False
    inList = False
    queryExist = True

    role_mapping = getRoleMapping()
    print role_mapping

    # primal query word # with '-v/-n' suffix
    query0 = ''
    # second query word # with '-v/-n' suffix
    query1 = ''
    # with '-1' suffix if noun selects noun
    semanticRoleList = role_mapping[model][role]

    # Adding suffix according to different types of query
    # Case of noun selects verb
    if group == 'noun':
        query0 = noun + '-n'
        semanticRoleList = [r + '-1' for r in semanticRoleList]
        if verb:
            double = True
            query1 = verb + '-v'
    # Case of verb selects noun
    elif group == 'verb':
        query0 = verb + '-v'
        semanticRoleList = semanticRoleList
        if noun:
            double = True
            query1 = noun + '-n'
    else:
        logger.critical( 'errCode: %d. internal error!', errorCode.INTERNAL_ERROR)
        result = {'errCode' : errorCode.INTERNAL_ERROR}
        return result

    # LOG
    # logger.debug('query0: %s' , query0)
    # logger.debug('query1: %s' , query1)
    # logger.debug('semanticRole: %s' , semanticRole)
    # logger.debug('group: %s' , group)
    # logger.debug('top_results: %d' , topN)

    print 'query0: %s' , query0
    print 'query1: %s' , query1
    print 'semanticRole: %s' , semanticRoleList
    print 'group: %s' , group
    print 'top_results: %d' , topN


    # memberTuple[0]: list of vectors
    # memberTuple[1]: list of words
    memberTuple = matrix.getMemberVectors(query0, 'word1', 'word0', {'link':semanticRoleList}, topN)

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
    print wordList

    sumWordList = list(wordList)
    resultList = []
    queryFraction = 0
    queryCosine = 0
    sumSupport = 0
    sumFraction = 0

    # Compute centroid from the vectorList using pandas
    centroid = pd.concat(vectorList).sum(level=[0,1])


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
            vector = query.ix[semanticRoleList[0]]
            if vector.get(query0, 0) == 0:
                # For the second query word, in this semantic role, the primal query word does not exist
                queryCosine = cosine_sim(centroid, query)
                queryExist = False
                logger.info('query.ix[semanticRole].ix[query0] is empty')
            else:
                if query1 not in sumWordList:
                    queryFraction = -1
                    queryCosine = cosine_sim(centroid, query)
                    wordVectors[query1] = query
                    sumWordList.append(query1)
                else:
                    inList = True
        except KeyError:
            # Semantic role of second query word does not exist
            logger.error( 'errCode: %d. query.ix[semanticRole] is empty', errorCode.SMT_ROLE_EMPTY)
            result = {'errCode' : errorCode.SMT_ROLE_EMPTY}
            return result

    # Obtain all supports and compute the sum support 
    for w in sumWordList:
        v = wordVectors[w]
        support = v.ix[semanticRoleList[0]].ix[query0]
        sumSupport = sumSupport + support
        wordSupports[w] = support

    wordList.reverse()

    # if there are 2 query words
    if double and not inList: 
        if queryExist:
            support = wordSupports[query1]
            queryFraction = float(support) / sumSupport
            sumFraction = queryFraction + sumFraction
        else:
            support = 0
            queryFraction = 0
            sumFraction = queryFraction + sumFraction
        q_x, q_y = mapping(queryFraction, queryCosine, sumFraction)

    for w in wordList:
    # Computer fraction and cosine
    # If the mapping function is changed, this must be changed
        fraction = float(wordSupports[w]) / sumSupport
        sumFraction = fraction + sumFraction
        wordCosine = cosine_sim(centroid, wordVectors[w])

        # Apply mapping to each word
        if inList and w == query1:
            # Apply mapping to second query word
            queryCosine = wordCosine
            q_x, q_y = mapping(fraction, wordCosine, sumFraction)
        else:
            x, y = mapping(fraction, wordCosine, sumFraction)

            # simularities[w] = wordCosine
            # fractions[w] = fraction

            print w, wordCosine, fraction, sumFraction

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

    if double:
        result['queried'] = {
            'y'    : q_y,
            'x'    : q_x,
            'cos'  : queryCosine,
            'word' : query1,
        }

    logger.info('result creating is prepared')

    return result


def mapping_1d(fraction, cosine, sumFraction):
    '''
    Mapping from fraction, and cosine to the x, y coordinate.
    This is a simple function which maps the high dimension vector to 2D.
    It is suitable for a web tool which need a short response time.

    @parameters:
        fraction = support / sumSupport
        cosine   = cosine_sim(centroid, wordVector)
    @return: 
        (x, y) is a tuple
    '''
    # Scale fraciton and cosine, let them become more sparse over [0, 1]
    x = 1 - (sumFraction - fraction)
    y = 1 - cosine

    # print x, y

    # Compute radial coordinates
    r = math.sqrt((math.pow(x, 2) + math.pow(y, 2))/2)
    if x - 0 < 1e-3:
        rad_b = math.pi / 2
    else:
        # Scale rad from [0, pi/2] to [0, 2 * pi]
        rad_b = math.atan(y / x)
    rad = rad_b

    # Transform back to Cartesian coordinates
    x = r * math.cos(rad)
    y = r * math.sin(rad)

    return x, y


def mapping(fraction, cosine, sumFraction):
    '''
    Mapping from fraction, and cosine to the x, y coordinate.
    This is a simple function which maps the high dimension vector to 2D.
    It is suitable for a web tool which needs a short response time.

    @parameters:
        fraction = support / sumSupport
        cosine   = cosine_sim(centroid, wordVector)
    @return: 
        (x, y) is a tuple
    '''
    # Scale fraciton and cosine, let them become more sparse over [0, 1]
    x = 1 - sumFraction
    y = 1 - cosine
    weight = 0.5

    # Compute radial coordinates
    r = math.sqrt(((1 - weight) * math.pow(x, 2) + weight * math.pow(y, 2))/2)
    
    rad_b = math.atan2( weight * y, ((1 - weight) * x))

    rad = rad_b * 4

    # Transform back to Cartesian coordinates
    x = r * math.cos(rad)
    y = r * math.sin(rad)

    return x, y
