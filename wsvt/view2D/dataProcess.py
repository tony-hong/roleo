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
from embeddingFactory import EmbeddingFactory
from roleDict import getRoleMapping

mf = MatrixFactory()
eb = EmbeddingFactory()
logger = logging.getLogger('django')


def getVector(vec, role):
    try:
        return vec.ix[role]
    except KeyError, e:
        return pd.DataFrame().sum()

def getSupport(vec, role, word1):
    try:
        return vec.ix[role].ix[word1]
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
    embeddingUsed = False

    modelList = model.split('_')
    modelName = modelList[0]
    matrix = mf.getMatrix(modelName)
    if modelName == 'RBE':
        embeddingUsed = True
        embedding = eb.getEmbedding()
        vocabulary = eb.getVocabulary()

        if vocabulary == -1:
            logger.critical( 'errCode: %d. internal error!', errorCode.INTERNAL_ERROR)
            result = {'errCode' : errorCode.INTERNAL_ERROR}
            return result


    wordVectors = dict()
    expandedVectors = dict()
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
    roleList = role_mapping[modelName][role]

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

    queryFraction = 0
    queryCosine = 0

    if embeddingUsed:
        roleParts = roleList[0].split('-')
        roleName = roleParts[0]

        # list of words
        wordList = matrix.getMemberList(queryWord0, 'word1', 'word0', {'link':roleList}, topN)

        # A hack checking whether the return is empty
        # if it is not list(), it is empty, the model return nothing for the primal query word
        if type(wordList) != type(list()):
            logger.error('errCode: %d. memberVectors is empty', errorCode.MBR_VEC_EMPTY)
            result = {'errCode' : errorCode.MBR_VEC_EMPTY}
            return result

        # LOG
        logger.info('getMemberVectors finished...')
        print wordList

        vectorList = list()
        temp = embedding['A0'][0]
        vectorSum = np.zeros(len(temp))

        for w in wordList:
            wordParts = w.split('-')
            wordName = wordParts[0]
            wordIndex = vocabulary.get(wordName, -1)

            if wordIndex == -1:
                # Second query word does not exist in the model
                logger.error( 'errCode: %d. Returned word in Malt is not in word embedding', errorCode.INTERNAL_ERROR)
                result = {'errCode' : errorCode.INTERNAL_ERROR}
                return result

            wordArray = embedding[roleName][wordIndex]
            vectorSum = vectorSum + wordArray
            vectorList.append(wordArray)

        # Reshape wordList, vectorList to a dict(), with key is word and value is vector
        wordVectors = dict(zip(wordList, vectorList))

        centroid = np.multiply(vectorSum, 1.0 / topN)
        
        query = np.zeros(len(temp)) 

        # if there are 2 query words, process the second query word
        if queryWord1:
            # process query
            queryWord = (queryWord1.split('-'))[0]
            queryIndex = vocabulary.get(queryWord, -1)

            logger.info('getting query finished')

            if queryIndex == -1:
                # Second query word does not exist in the model
                logger.error( 'errCode: %d. query is empty', errorCode.QUERY_EMPTY)
                result = {'errCode' : errorCode.QUERY_EMPTY}
                return result
            else:
                query = embedding[roleName][queryIndex]
                queryCosine = cosine_sim(centroid, query)
                wordVectors[queryWord1] = query
                if queryWord1 in wordList:
                    inList = True

    else:
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

        query = pd.Series()

        # if there are 2 query words, process the second query word
        if queryWord1:
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


    if quadrant < 0:
        result = svd_cosine(wordList, wordVectors, centroid, queryWord1, queryCosine, quadrant)
    else:
        result = fraction_cosine(wordList, wordVectors, roleList, query, centroid, queryWord0, queryWord1, queryCosine, quadrant)

    result['quadrant'] = quadrant

    return result



def fraction_cosine(wordList, wordVectors, roleList, query, centroid, queryWord0, queryWord1, queryCosine, quadrant):
    sumFraction = 0

    resultList = []
    wordSupports = dict()

    centroidSupport = sum([getSupport(centroid, r, queryWord0) for r in roleList])
    # vectorSum = pd.concat([getVector(query, r) for r in roleList]).sum(level = 0)
    querySupport = sum([getSupport(query, r, queryWord0) for r in roleList])
    wordSupports[queryWord1] = querySupport

    queryFraction = float(querySupport) / centroidSupport
    sumFraction = sumFraction + queryFraction

    q_x, q_y = ms.mapping([queryFraction, queryCosine, sumFraction], quadrant)

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
            q_x, q_y = ms.mapping([fraction, wordCosine, sumFraction], quadrant)
        else:
            x, y = ms.mapping([fraction, wordCosine, sumFraction], quadrant)

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

    if queryWord1:
        result['queried'] = {
            'y'    : q_y,
            'x'    : q_x,
            'cos'  : queryCosine,
            'word' : queryWord1,
        }

    logger.info('result creating is prepared')

    return result



def svd_cosine(wordList, wordVectors, centroid, queryWord1, queryCosine, quadrant):
    temp = wordVectors[wordList[0]]
    if isinstance(temp, pd.Series): 
        base = pd.concat(wordVectors.values()).sum(level=[0,1])

        M = pd.DataFrame()
        index = 0
        resultList = []    
        wordDict = dict()

        # Obtain all supports and compute the sum support 
        for w in wordVectors.keys():
            s = pd.Series(base)

            s[:] = 0

            s = s + wordVectors[w] - centroid

            s.fillna(0, inplace=True)

            s.name = w
            wordDict[w] = index

            M = M.append(s)
            index = index + 1

    else:
        keys = wordVectors.keys()
        num = len(keys)
        M = np.zeros((num, 256))
        index = 0
        resultList = []    
        wordDict = dict()

        # Obtain all supports and compute the sum support 
        for w in keys:
            M[index] = wordVectors[w] - centroid
            wordDict[w] = index
            index = index + 1

    # subtract the mean of target matrix
    meanVals = np.mean(M, axis=0)
    M = M - meanVals
    
    # perform SVD
    U, sigma, V = np.linalg.svd(M, full_matrices=False, compute_uv=True)

    wordCosines = dict()
    minCosine = queryCosine if (queryCosine > 0) else 10

    for w in wordList:
        cos = cosine_sim(centroid, wordVectors[w])
        wordCosines[w] = cos
        minCosine = cos if (cos < minCosine) else minCosine

    for w in wordList:
        i = wordDict[w]

        cos = wordCosines[w]
        u = U[i]
        x0, y0 = u[0], u[1]

        x, y = ms.mapping([x0, cos, y0, minCosine], quadrant)

        resultList.append({
            'y'     : y,
            'x'     : x, 
            'cos'   : cos, 
            'word'  : w,
        })

    result = {
        'nodes'    : resultList,
    }

    if queryWord1:
        i = wordDict[queryWord1]
        
        # only consider top 2         
        qx0, qy0 = U[i][0], U[i][1]

        print queryWord1, qx0, qy0

        q_x, q_y = ms.mapping([qx0, queryCosine, qy0, minCosine], quadrant)
        result['queried'] = {
            'y'    : q_y,
            'x'    : q_x,
            'cos'  : queryCosine,
            'word' : queryWord1,
        }
        
        print queryWord1, q_x, q_y

    return result
