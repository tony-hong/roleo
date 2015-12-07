#!/usr/bin/python

import os
import sys
import pandas as pd
from numpy.linalg import norm

def ecu(centroid, vec, item, relations):
    pass

def cosine_sim(series1, series2):
    """
    takes two pandas Series and finds the cosine between them,
    even if they aren't aligned (it aligns them).
    """
    
    A, B = series1.align(series2)
    A = A.fillna(0)
    B = B.fillna(0)

    return A.dot(B)/(norm(A) * norm(B))

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
