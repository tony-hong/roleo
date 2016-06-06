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

import logging

import numpy as np
import pandas as pd

from rv.similarity.Similarity import cosine_sim

import errorCode as errorCode
import mappingSelector as ms
from matrixFactory import MatrixFactory
from roleDict import getRoleMapping

mf = MatrixFactory()
logger = logging.getLogger('django')


def getVector(word, role):
    try:
        return word.ix[role]
    except KeyError, e:
        return pd.DataFrame().sum()

def getSupport(word0, role, word1):
    try:
        return word0.ix[role].ix[word1]
    except KeyError, e:
        return 0



def processQuery(verb, noun, role, group, model, topN = 20, quadrant = 4):
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
    matrix = mf.getMatrix(model)

    wordVectors = dict()
    expandedVectors = dict()
    wordIndex = dict()
    result = dict()
    
    logger.info('process start...')

    memberIndex = dict()
    double = False
    inList = False
    queryExist = True

    role_mapping = getRoleMapping()

    # primal query word # with '-v/-n' suffix
    queryWord0 = ''
    # second query word # with '-v/-n' suffix
    queryWord1 = ''
    # with '-1' suffix if noun selects noun
    roleList = role_mapping[model][role]

    # Adding suffix according to different types of query
    # Case of noun selects verb
    if group == 'noun':
        queryWord0 = noun + '-n'
        roleList = [r + '-1' for r in roleList]
        if verb:
            double = True
            queryWord1 = verb + '-v'
    # Case of verb selects noun
    elif group == 'verb':
        queryWord0 = verb + '-v'
        roleList = roleList
        if noun:
            double = True
            queryWord1 = noun + '-n'
    else:
        logger.critical( 'errCode: %d. internal error!', errorCode.INTERNAL_ERROR)
        result = {'errCode' : errorCode.INTERNAL_ERROR}
        return result

    # memberTuple[0]: list of vectors
    # memberTuple[1]: list of words
    memberTuple = matrix.getMemberVectors(queryWord0, 'word1', 'word0', {'link':roleList}, topN)

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

    # Compute centroid from the vectorList using pandas
    centroid = pd.concat(vectorList).sum(level=[0,1])

    extendWordList = list(wordList)
    queryFraction = 0
    queryCosine = 0
    maxSupport = 0

    # if there are 2 query words, process the second query word
    if double:
        # process query
        query = matrix.getRow('word0', queryWord1)

        logger.info('getting query finished')

        if query.isnull().all():
            # Second query word does not exist in the model
            logger.error( 'errCode: %d. query is empty', errorCode.QUERY_EMPTY)
            result = {'errCode' : errorCode.QUERY_EMPTY}
            return result
        else:
            queryCosine = cosine_sim(centroid, query)
            wordVectors[queryWord1] = query
            if queryWord1 in wordList:
                inList = True

    if quadrant == -2:
        result = svd_cosine(wordList, wordVectors, centroid, queryWord1, double, queryCosine)
    else:
        result = fraction_cosine(wordList, wordVectors, roleList, query, centroid, queryWord0, queryWord1, double, queryCosine, quadrant)

    result['quadrant'] = quadrant

    return result



def fraction_cosine(wordList, wordVectors, roleList, query, centroid, queryWord0, queryWord1, double, queryCosine, quadrant):
    sumFraction = 0

    resultList = []
    wordIndex = dict()
    wordSupports = dict()

    centroidSupport = sum([getSupport(centroid, r, queryWord0) for r in roleList])
    # vectorSum = pd.concat([getVector(query, r) for r in roleList]).sum(level = 0)
    querySupport = sum([getSupport(query, r, queryWord0) for r in roleList])
    wordSupports[queryWord1] = querySupport

    queryFraction = float(querySupport) / centroidSupport
    sumFraction = sumFraction + queryFraction
    q_x, q_y = ms.mapping(queryFraction, queryCosine, sumFraction, quadrant)

    wordList.reverse()

    # Obtain all supports and compute the sum support
    for w in wordList:
        v = wordVectors[w]
        support = sum([getSupport(v, r, queryWord0) for r in roleList])
        wordSupports[w] = support
    
    # Computer fraction and cosine
    for w in wordList:
        v = wordVectors[w]
        # If the mapping function is changed, this must be changed
        fraction = float(wordSupports[w]) / centroidSupport
        sumFraction = fraction + sumFraction
        wordCosine = cosine_sim(centroid, v)

        # Apply mapping to each word
        if w == queryWord1:
            # Apply mapping to second query word
            q_x, q_y = ms.mapping(fraction, wordCosine, sumFraction, quadrant)
        else:
            x, y = ms.mapping(fraction, wordCosine, sumFraction, quadrant)

            # simularities[w] = wordCosine
            # fractions[w] = fraction

            # print w, wordCosine, fraction, sumFraction

            resultList.append({
                'y'     : y,
                'x'     : x, 
                'cos'   : wordCosine, 
                'word'  : w,
            })

    # if not inList:

    logger.info('result list is prepared')

    result = {
        'nodes'    : resultList,
        'quadrant' : quadrant
    }

    if double:
        result['queried'] = {
            'y'    : q_y,
            'x'    : q_x,
            'cos'  : queryCosine,
            'word' : queryWord1,
        }

    logger.info('result creating is prepared')

    return result




def svd_cosine(wordList, wordVectors, centroid, queryWord1, double, queryCosine):
    # set up a base vector containing all features of top n returned and the query vector
    base = pd.concat(wordVectors.values()).sum(level=[0,1])

    M = pd.DataFrame()
    index = 0
    resultList = []    
    wordIndex = dict()

    # expand all vectors to the dimension of the base

    for w in wordVectors.keys():
        s = pd.Series(base)

        s[:] = 0

        # minus centroid to make the centroid in the center
        s = s + wordVectors[w] - centroid

        s.fillna(0, inplace=True)

        s.name = w
        wordIndex[w] = index

        M = M.append(s)
        index = index + 1

    # subtract the mean of target matrix
    meanVals = np.mean(M, axis=0)
    M = M - meanVals

    # perform SVD
    U, sigma, V = np.linalg.svd(M, full_matrices=False, compute_uv=True)

    for w in wordList:
        i = wordIndex[w]

        u = U[i]
        x0, y0 = u[0], u[1]

        wordCosine = cosine_sim(centroid, wordVectors[w])

        x, y = ms.mapping(x0, wordCosine, y0, -1)

        resultList.append({
                'y'     : y,
                'x'     : x, 
                'cos'   : wordCosine, 
                'word'  : w,
            })

    result = {
        'nodes'    : resultList,
    }

    if double:
        i = wordIndex[queryWord1]

        # only consider top 2 
        qx0, qy0 = U[i][0], U[i][1]

        print queryWord1, qx0, qy0

        q_x, q_y = ms.mapping(qx0, queryCosine, qy0, -2)
        result['queried'] = {
            'y'    : q_y,
            'x'    : q_x,
            'cos'  : queryCosine,
            'word' : queryWord1,
        }
        
        print queryWord1, q_x, q_y

    return result

