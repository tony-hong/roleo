#!/usr/bin/python

import os
import sys
import numpy as np
import pandas as pd

from numpy.linalg import norm


def ecu(centroid, vec, item, relations):
    pass

def ecu_dist(series1, series2):
    """
    Takes two pandas Series and finds the euclidean distance between them,
    even if they aren't aligned (it aligns them).
    """
    A, B = series1.align(series2)
    A = A.fillna(0)
    B = B.fillna(0)

    return norm(A / norm(A) - B / norm(B))

def cosine_sim(vector1, vector2):
    """
    Takes two pandas Series or numpy array and finds the cosine between them,
    even if they aren't aligned (it aligns them).
    """
    if isinstance(vector1, pd.Series):
        A, B = vector1.align(vector2)
        A = A.fillna(0)
        B = B.fillna(0)
    else:
        A = vector1
        B = vector2
    return A.dot(B)/(norm(A) * norm(B))

    return result

def sim_inv_mag(M):
    '''
    Compute similarity matrix and the inverse of the magnitude on its diagonal for vectors.
    The 'M' is a matrix containing input vectors.    
    '''
    # base similarity matrix (all dot products)
    # replace this with A.dot(A.T).todense() for sparse representation
    similarity = np.dot(M, M.T)
    # squared magnitude of preference vectors (number of occurrences)
    square_mag = np.diag(similarity)
    # inverse squared magnitude
    inv_square_mag = 1 / square_mag
    # if it doesn't occur, set it's inverse magnitude to zero (instead of inf)
    inv_square_mag[np.isinf(inv_square_mag)] = 0
    # inverse of the magnitude
    inv_mag = np.sqrt(inv_square_mag)

    return similarity, inv_mag


def cosine_sim_mat(M):
    '''
    Compute cosine similarity matrix for vectors.
    The 'M' is a matrix containing input vectors.
    The return is a cosine similarity matrix containing similarities between all input vectors. The indices are the same with input.
    '''
    similarity, inv_mag = sim_inv_mag(M)

    # cosine similarity (elementwise multiply by inverse magnitudes)
    cosine = similarity * inv_mag
    cosine = cosine.T * inv_mag

    return cosine

def cosine_sim_mat_n(M):
    '''
    Compute cosine similarity matrix and normalisation for vectors
    The 'M' is a matrix containing input vectors.
    The return is a cosine similarity matrix containing similarities between all input vectors. The indices are the same with input.
    '''
    similarity, inv_mag = sim_inv_mag(M)

    # cosine similarity (elementwise multiply by inverse magnitudes)
    cosine = similarity * inv_mag
    cosine = cosine.T * inv_mag

    # normalize all vectors
    B = M * inv_mag.reshape(len(inv_mag), 1)

    return cosine, B


def vector_sum(vecs, level=None):
    """
    Efficient summing for a set of vectors as pd.DataFrame.
    """
    if level:
        return pd.concat(vecs).sum(level=level)
    else:
        return pd.concat(vecs).sum()


class Target:
    '''
    This class represents the item being explored in the tensor
    for its connections to other items.
    '''

    def __init__(self, tensor, colname, item):
        self.tensor = tensor
        self.item = item
        self.colname = colname
        self.roledict = {}

    def registerRole(self, colname, categories, valcol):
        pass

if __name__ == "__main__":
    from Tensor import Tensor

    if len(sys.argv) < 5:
        print >>sys.stderr, "Syntax: Similarity.py db.h5 tablename verb argument"
        sys.exit(-1)

    tensor = Tensor(sys.argv[1], sys.argv[2])
    T1 = tensor.getCentroid({'link':['nsubj'], 'word0':sys.argv[3]}, 'lmi')
    T2 = tensor.getCentroid({'link':['dobj'], 'word0':sys.argv[3]}, 'lmi')
    R = tensor.getRow('word0', sys.argv[4], 'lmi')

    print "As subject", cosine_sim(T1, R.ix[sys.argv[4]])
    print "As object", cosine_sim(T2, R.ix[sys.argv[4]])

    tensor.close()
