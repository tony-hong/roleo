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
import math

import numpy as np
import pandas as pd
from sklearn import (manifold, datasets, decomposition, ensemble,
                         discriminant_analysis, random_projection)

from rv.similarity.Similarity import cosine_sim, cosine_sim_mat, mat_n

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

    if modelName == 'RBE' or modelName == 'W2V':
        embeddingUsed = True
        embedding = eb.getEmbedding(modelName)
        vocabulary = eb.getVocabulary()

        if vocabulary == -1:
            logger.critical( 'errCode: %d. internal error!', errorCode.INTERNAL_ERROR)
            return {'errCode' : errorCode.INTERNAL_ERROR}


    wordVectors = dict()
    result = dict()
    
    logger.info('process start...')

    inList = False

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
            queryWord1 = verb + '-v'
    # Case of verb selects noun
    elif group == 'verb':
        queryWord0 = verb + '-v'
        roleList = roleList
        if noun:
            queryWord1 = noun + '-n'
    else:
        logger.critical( 'errCode: %d. internal error!', errorCode.INTERNAL_ERROR)
        return {'errCode' : errorCode.INTERNAL_ERROR}

    queryFraction = 0
    queryCosine = 0

    if embeddingUsed:
        roleParts = roleList[0].split('-')
        if len(roleParts) == 1:
            roleName = roleParts[0]
        elif len(roleParts) == 2:
            if roleParts[1] == '1':
                roleName = roleParts[0]
            else:
                roleName = roleParts[0] + '-' + roleParts[1]
        else:
            roleName = roleParts[0] + '-' + roleParts[1]

        # list of words
        wordList = matrix.getMemberList(queryWord0, 'word1', 'word0', {'link':roleList}, topN)

        # A hack checking whether the return is empty
        # if it is not list(), it is empty, the model return nothing for the primal query word
        if len(wordList) == 0:
            logger.error('errCode: %d. memberVectors is empty', errorCode.MBR_VEC_EMPTY)
            return {'errCode' : errorCode.MBR_VEC_EMPTY}

        # LOG
        logger.info('getMemberVectors finished...')
        print wordList

        vectorList = list()
        if modelName == 'RBE':
            temp = embedding['A0'][0]
        else:
            temp = embedding['A0']['apple']

        vectorSum = np.zeros(len(temp))

        tempList = list()

        for w in wordList:
            wordParts = w.split('-')
            wordName = wordParts[0]
            wordIndex = vocabulary.get(wordName, -1)

            if wordIndex == -1:
                continue

            if modelName == 'RBE':
                wordArray = embedding[roleName][wordIndex]
            else:
                wordArray = embedding[roleName].get(wordName, -1)
                if type(wordArray) == type(1):
                    continue

            vectorSum = vectorSum + wordArray
            tempList.append(w)
            vectorList.append(wordArray)

        wordList = tempList

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
                return {'errCode' : errorCode.QUERY_EMPTY}
            else:
                if modelName == 'RBE':
                    query = embedding[roleName][queryIndex]
                else:
                    query = embedding[roleName].get(queryWord, -1)
                    if type(query) == type(1):
                        logger.error( 'errCode: %d. query is empty', errorCode.QUERY_EMPTY)
                        return {'errCode' : errorCode.QUERY_EMPTY}

                queryCosine = cosine_sim(centroid, query)
                wordVectors[queryWord1] = query
                if queryWord1 in wordList:
                    inList = True

    else:
        # memberTuple[0]: list of vectors
        # memberTuple[1]: list of words
        memberTuple = matrix.getMemberVectors(queryWord0, 'word1', 'word0', {'link':roleList}, topN)
        vectorList, wordList = memberTuple
        
        # A checking whether the return is empty
        if len(wordList) == 0:
            logger.error('errCode: %d. memberVectors is empty', errorCode.MBR_VEC_EMPTY)
            return {'errCode' : errorCode.MBR_VEC_EMPTY}

        # LOG
        logger.info('getMemberVectors finished...')
        # print wordList

        # Reshape wordList, vectorList to a dict(), with key is word and value is vector
        wordVectors = dict(zip(wordList, vectorList))

        # Compute centroid from the vectorList using pandas
        centroid = pd.concat(vectorList).sum(level=[0,1])
        base = centroid

        query = pd.Series()

        # if there are 2 query words, process the second query word
        if queryWord1:
            # process query
            query = matrix.getRow('word0', queryWord1)

            logger.info('getting query finished')

            if query.isnull().all():
                # Second query word does not exist in the model
                logger.error( 'errCode: %d. query is empty', errorCode.QUERY_EMPTY)
                return {'errCode' : errorCode.QUERY_EMPTY}
            else:
                queryCosine = cosine_sim(centroid, query)
                wordVectors[queryWord1] = query
                base = centroid.align(query)[0]
                if queryWord1 in wordList:
                    inList = True
    
    if quadrant < 0:
        if not embeddingUsed:
            for w in wordVectors.keys():
                v = wordVectors[w]
                v = v.align(base)[0]
                wordVectors[w] = v.fillna(0).values
            centroid = base.fillna(0).values
        result = svd_cosine(wordList, wordVectors, centroid, queryWord1, queryCosine, quadrant)
    else:
        result = fraction_cosine(wordList, wordVectors, roleList, centroid, queryWord0, queryWord1, queryCosine, quadrant)

    result['quadrant'] = quadrant

    return result

def fraction_cosine(wordList, wordVectors, roleList, centroid, queryWord0, queryWord1, queryCosine, quadrant):
    sumFraction = 0
    maxValue = 1

    resultList = []
    wordSumFractions = dict()
    wordCosines = dict()

    N = len(wordList)
    D = len(centroid)

    centroidSupport = sum([getSupport(centroid, r, queryWord0) for r in roleList])

    if queryWord1:
        query = wordVectors[queryWord1]
        querySupport = sum([getSupport(query, r, queryWord0) for r in roleList])
        queryFraction = float(querySupport) / centroidSupport
        sumFraction = sumFraction + queryFraction
        q_x, q_y = ms.mapping([queryFraction, queryCosine, 1 - min(queryFraction, queryCosine)], quadrant)

    wordList.reverse()

    A = np.zeros((N + 1, D))
    i = 0

    # Obtain all supports and compute the sum support
    for w in wordList:
        v = wordVectors[w]

        v = (wordVectors[w]).align(centroid)[0]
        v.fillna(0, inplace=True)
        a = v.values
        a = a / np.sqrt(np.square(a).sum())
        A[i] = a 
        i = i + 1

        support = sum([getSupport(v, r, queryWord0) for r in roleList])
    
        # Computer fraction and cosine
        # If the mapping function is changed, this must be changed
        fraction = float(support) / centroidSupport
        sumFraction = fraction + sumFraction

        wordSumFractions[w] = sumFraction

        # wordCosine = cosine_sim(centroid, v)
        # wordCosines[w] = wordCosine

    centroidVec = sum(A) / N
    A[N] = centroidVec

    cosines = cosine_sim_mat(A)
    i = 0
    for w in wordList:
        wordCosines[w] = cosines[N][i]
        i = i + 1

    # for auto-scaling 
    maxValue = 1 - min(min(wordSumFractions.values()), min(wordCosines.values()))

    for w in wordList:

        # Apply mapping to each word
        if queryWord1 and w == queryWord1:
            # Apply mapping to second query word
            q_x, q_y = ms.mapping([wordSumFractions[w], wordCosines[w], maxValue], quadrant)
        else:
            x, y = ms.mapping([wordSumFractions[w], wordCosines[w], maxValue], quadrant)

            resultList.append({
                'y'     : y,
                'x'     : x, 
                'cos'   : wordCosines[w], 
                'word'  : w,
            })

    logger.info('result list is prepared')

    result = {
        'nodes'    : resultList,
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
    keys = wordVectors.keys()
    N = len(keys)
    D = len(temp)
    B = np.zeros((N, D))
    M = np.zeros((N, D))
    A = np.zeros((N + 1, D))

    index = 0
    resultList = []
    wordDict = dict()

    # Obtain all supports and compute the sum support 
    for w in keys:
        v = wordVectors[w]
        B[index] = v
        wordDict[w] = index
        index = index + 1

    M = mat_n(B)
    centroid = sum(M) / N
    
    for w in keys:
        i = wordDict[w]
        A[i] = M[i]
    A[N] = centroid

    cosines = cosine_sim_mat(A)

    # import cPickle
    # print "\nSaving cPickle..."
    # with open("vectors.pcl", 'wb') as f:
    #     cPickle.dump(M, f, cPickle.HIGHEST_PROTOCOL)
    
    n_neighbors = N - 1

    if quadrant == -1 or quadrant == -2:
        # SVD

        # subtract the centroid of target matrix
        M = M - centroid

        # perform SVD
        U, sigma, V = np.linalg.svd(M, full_matrices=False, compute_uv=True)

    elif quadrant == -3 or quadrant == -4:
        # isomap, best clusters
        U = manifold.Isomap(n_neighbors, n_components=2).fit_transform(M)

    elif quadrant == -5 or quadrant == -6:
        # Local Tangent Space Alignment (ltsa), 
        clf = manifold.LocallyLinearEmbedding(n_neighbors, n_components=2, method='ltsa')
        U = clf.fit_transform(M)

    elif quadrant == -7 or quadrant == -8:
        # MDS, circle like structure
        clf = manifold.MDS(n_components=2, n_init=1, max_iter=100)
        U = clf.fit_transform(M)
        
    elif quadrant == -9 or quadrant == -10:
        # use precomputed cosine distances to speed up t-SNE, restrict the iteration to 200
        tsne = manifold.TSNE(random_state = 0, n_iter=200, metric='precomputed')

        cosine_dists = np.arccos(cosines) / math.pi
        print cosine_dists

        U = tsne.fit_transform(np.around(cosine_dists, decimals=8))

    else:
        # Spectral Embedding, bad
        embedder = manifold.SpectralEmbedding(n_components=2, random_state=0, eigen_solver="arpack")
        U = embedder.fit_transform(M)




    wordCosines = dict()
    wordX = dict()
    wordY = dict()

    minCosine = queryCosine if (queryCosine > 0) else 10
    maxVal = -1

    for w in wordList:
        i = wordDict[w]
        u = U[i]
        cos = cosines[N][i]

        wordX[w] = u[0]
        wordY[w] = u[1]
        wordCosines[w] = cos

        minCosine = cos if (cos < minCosine) else minCosine
        r = math.sqrt(u[0] * u[0] + u[1] * u[1])
        maxVal = r if (r > maxVal) else maxVal

    if queryWord1:
        i = wordDict[queryWord1]
        
        # only consider top 2
        qx0, qy0 = U[i][0], U[i][1]
        queryCosine = cosines[N][i]

        r = math.sqrt(qx0 * qx0 + qy0 * qy0)
        maxVal = r if (r > maxVal) else maxVal

    for w in wordList:
        cos = wordCosines[w]
        x0, y0 = wordX[w], wordY[w]

        x, y = ms.mapping([x0, y0, cos, minCosine, maxVal], quadrant)


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
        q_x, q_y = ms.mapping([qx0, qy0, queryCosine, minCosine, maxVal], quadrant)

        result['queried'] = {
            'y'    : q_y,
            'x'    : q_x,
            'cos'  : queryCosine,
            'word' : queryWord1,
        }
        

    return result
