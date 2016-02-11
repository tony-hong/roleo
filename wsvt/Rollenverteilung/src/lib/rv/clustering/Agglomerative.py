#!/usr/bin/python

import pandas as pd
import numpy
from nltk.cluster import GAAClusterer
from nltk.cluster.util import cosine_distance

def undoSparseness(top) :
    '''creates a numpy array from a list of pandas series objects'''
    centroid = pd.concat(top).sum(level=[0,1])
    orig = []
    #i = 1
    for vec in top:
        A, B = centroid.align(vec)
        B = B.fillna(0)
        orig.append(B)
        #print "done with " + str(i)
        #i += 1
    return numpy.array(orig)

def redoSparseness(top, vectoword, k, gaac) :
    '''creates a list of pandas series objects from a cluster assignment'''
    groups = []
    humanGroups = []
    for i in range(k) : 
        groups.append([])
        humanGroups.append([])

    for i in range(len(top)) : 
        groups[gaac[i]].append(top[i])
        humanGroups[gaac[i]].append(vectoword[i])

    for i in range(k) :
        if len(groups[i]) == 0 : raise ValueError
        else : groups[i] = pd.concat(groups[i]).sum(level=[0,1])

    return (groups, humanGroups)

def Clustering(orig, minclusters, maxclusters) :
    '''returns (distortion score, number of clusters, cluster assignment)'''

    # perform clustering
    clusterer = GAAClusterer()
    clusterer.cluster(orig)
    vrc = []

    # calculate distortions
    wb = len(orig)
    centroid = numpy.mean(orig, axis=0)
    for vector in orig : wb -= cosine_distance(vector, centroid)
    lowerbound = minclusters
    if lowerbound < 2 : lowerbound = 2
    for k in range(lowerbound, maxclusters + 1) :
        clusterer.update_clusters(k)
        gaac = []
        ww = len(orig)
        for vector in orig :
            maxcos = None
            for j in range(k) :
                clust = clusterer._centroids[j]
                cdist = cosine_distance(vector, clust)
                if not maxcos or cdist > maxcos[0] :
                    maxcos = (cdist, j)
            ww -= maxcos[0]
            gaac.append(maxcos[1])
        vrc.append(((wb/(k - 1)) / (ww/(len(orig) - k)), k, gaac))
    khat = (float("inf"), vrc[0][1], vrc[0][2])
    for k in range(1, len(vrc) - 1) :
        dist = (vrc[k+1][0] - vrc[k][0]) - (vrc[k][0] - vrc[k-1][0])
        if dist < khat[0] : khat = (dist, vrc[k][1], vrc[k][2])

    return khat
