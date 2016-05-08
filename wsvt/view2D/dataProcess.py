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


def process(verb, noun, role, group, model, topN = 20, quadrant = 4):
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

    # LOG
    # logger.debug('queryWord0: %s' , queryWord0)
    # logger.debug('queryWord1: %s' , queryWord1)
    # logger.debug('semanticRole: %s' , semanticRole)
    # logger.debug('group: %s' , group)
    # logger.debug('top_results: %d' , topN)

    # print 'queryWord0: %s' , queryWord0
    # print 'queryWord1: %s' , queryWord1
    # print 'semanticRole: %s' , roleList
    # print 'group: %s' , group
    # print 'top_results: %d' , topN


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
    print wordList

    sumWordList = list(wordList)
    resultList = []
    queryFraction = 0
    queryCosine = 0
    sumSupport = 0
    maxSupport = 0
    sumFraction = 0
    centroidSupport = 0

    # Compute centroid from the vectorList using pandas
    centroid = pd.concat(vectorList).sum(level=[0,1])
    centroidSupport = sum([getSupport(centroid, r, queryWord0) for r in roleList])

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
            vector = pd.concat([getVector(query, r) for r in roleList]).sum(level = 0)
            if vector.get(queryWord0, 0) == 0:
                # For the second query word, with this semantic role, the primal query word does not exist
                queryCosine = cosine_sim(centroid, query)
                queryExist = False
                logger.info('vector for queryWord0 is empty')
            else:
                if queryWord1 not in sumWordList:
                    queryFraction = -1
                    queryCosine = cosine_sim(centroid, query)
                    wordVectors[queryWord1] = query
                    sumWordList.append(queryWord1)
                else:
                    inList = True

    # Obtain all supports and compute the sum support 
    for w in sumWordList:
        v = wordVectors[w]
        support = sum([getSupport(v, r, queryWord0) for r in roleList])
        sumSupport = sumSupport + support
        wordSupports[w] = support

    wordList.reverse()

    # if there are 2 query words
    if double and not inList: 
        if queryExist:
            support = wordSupports[queryWord1]
            queryFraction = float(support) / centroidSupport
            sumFraction = queryFraction + sumFraction
        else:
            support = 0
            queryFraction = 0
            sumFraction = queryFraction + sumFraction
        q_x, q_y = ms.mapping(queryFraction, queryCosine, sumFraction, quadrant)

    for w in wordList:
    # Computer fraction and cosine
    # If the mapping function is changed, this must be changed
        fraction = float(wordSupports[w]) / centroidSupport
        sumFraction = fraction + sumFraction
        wordCosine = cosine_sim(centroid, wordVectors[w])

        # Apply mapping to each word
        if inList and w == queryWord1:
            # Apply mapping to second query word
            queryCosine = wordCosine
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





def process_svd(verb, noun, role, group, model, topN = 20, quadrant = 4):
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
    wordSupports = dict()
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

    sumWordList = list(wordList)
    resultList = []
    queryFraction = 0
    queryCosine = 0
    sumSupport = 0
    maxSupport = 0
    sumFraction = 0
    centroidSupport = 0

    # Compute centroid from the vectorList using pandas
    centroid = pd.concat(vectorList).sum(level=[0,1])
    centroidSupport = sum([getSupport(centroid, r, queryWord0) for r in roleList])

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
            vector = pd.concat([getVector(query, r) for r in roleList]).sum(level = 0)
            if vector.get(queryWord0, 0) == 0:
                # For the second query word, with this semantic role, the primal query word does not exist
                queryCosine = cosine_sim(centroid, query)
                queryExist = False
                logger.info('vector for queryWord0 is empty')
            else:
                if queryWord1 not in sumWordList:
                    queryFraction = -1
                    queryCosine = cosine_sim(centroid, query)
                    wordVectors[queryWord1] = query
                    sumWordList.append(queryWord1)
                else:
                    inList = True


    base = pd.concat(wordVectors.values()).sum(level=[0,1])

    M = pd.DataFrame()
    index = 0
    mean = centroid #.div(len(wordList))


    # Obtain all supports and compute the sum support 
    for w in sumWordList:
        s = pd.Series(base)

        s[:] = 0

        s = s + wordVectors[w] - mean

        s.fillna(0, inplace=True)

        s.name = w
        wordIndex[index] = w

        # print '\n s: \n'
        # print s
        # print '\n M before: \n' 
        # print M

        M = M.append(s)
        index = index + 1

    # print '\n M after: \n' 
    # print M

    # print '\n M final: \n' 
    # print M.as_matrix()

    meanVals = np.mean(M, axis=0)
    M = M - meanVals
    
    U, sigma, V = np.linalg.svd(M, full_matrices=False, compute_uv=True)
    
    # print '\n U: \n' 
    # print U

    # print '\n sigma: \n' 
    # print sigma

    for i in range(len(U) - 1):
        u = U[i]
        x, y = u[0], u[1]

        # print wordIndex[i], x, y

        wordCosine = cosine_sim(centroid, wordVectors[wordIndex[i]])

        resultList.append({
                'y'     : y,
                'x'     : x, 
                'cos'   : wordCosine, 
                'word'  : wordIndex[i],
            })

    q_x, q_y = U[len(U) - 1][0], U[len(U) - 1][1]

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

    return result


