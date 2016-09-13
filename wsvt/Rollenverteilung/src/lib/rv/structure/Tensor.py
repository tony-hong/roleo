#!/usr/bin/python

import sys
import os
import pandas as pd
import numpy as np
import numpy.linalg as nla
import gc

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class Tensor:
    def __init__(self, hdfstore, tablename):
        if isinstance(hdfstore, pd.HDFStore):
            self.store = hdfstore
        else:
            self.store = pd.HDFStore(hdfstore, "r")

        self.tablename = tablename

    def getCentroid(self, targetdict, valcol, topN=20):
        # get the rows.
        query = [pd.Term(key, "=", value) for key, value in targetdict.iteritems()]
        selectdf = self.store.select(self.tablename, where=query)

        # pivot the table.
        colindex = [x for x in selectdf.columns if x not in targetdict.keys() + [valcol]]
        pivotdf = selectdf.pivot_table(valcol, targetdict.keys(), colindex).fillna(0)

        ## unit-vectorize the pivot table.  The *columns* are treated as the vectors.
        #for col in pivotdf.columns:
        #    pivotdf[col] = nla.norm(pivotdf[col])

        # The columns are the vectors.  Return the topN columnheads by length.
        pivotdf = pivotdf.apply(lambda x: nla.norm(x))
        
        # FIXED: sort is deprecated
        # pivotdf.sort(ascending=False)
        pivotdf.sort_values(inplace=True, ascending=False)

        topcols = list(pivotdf[:topN].index)
        if not topcols:
            return None
        topcols = [x.replace('"', "\\\"") for x in topcols]

        #print >>sys.stderr, pivotdf

        # Now use the topN to get relevant rows for the colindex.
        query = [pd.Term(colindex[n], "=", topcols) 
                 for n in range(0, len(colindex))]
        #print >>sys.stderr, repr(query)

        # Now create the centroid based on the colindex.
        selectdf = self.store.select(self.tablename, where=query)
        pivotdf = selectdf.pivot_table(valcol, colindex, sorted(targetdict.keys())).fillna(0)

        return pivotdf.sum()

    def getRow(self, rowname, rowval, valcol):
        query = pd.Term(rowname, '=', rowval)
        selectdf = self.store.select(self.tablename, where=query)

        colindex = [x for x in selectdf.columns if x not in [rowname, valcol]]
        pivotdf = selectdf.pivot_table(valcol, rowname, sorted(colindex)).fillna(0)

        return pivotdf.sum() # need this to get a Series out.

    def aggregateDimension(self, colname, aggfunc=sum, chunksize=4000000):
        response = self.store.select(self.tablename, where=("columns=%s" % colname), chunksize=chunksize)
        aggregation = None
        for chunk in response:
            if aggregation:
                aggregation = aggfunc([aggregation, aggfunc(chunk[colname])])
            else:
                aggregation = aggfunc(chunk[colname])
            print >>sys.stderr, "Aggregation stands at %s." % repr(aggregation)

        return aggregation

    def uniqueDimension(self, colname, chunksize=2000000):
        response = self.store.select(self.tablename, where=("columns=%s" % colname), chunksize=chunksize)
        aggregation = set([])
        for chunk in response:
            aggregation.update(list(chunk[colname].unique()))
            print >>sys.stderr, "Number of unique items stands at %d." % len(aggregation)
        
        return aggregation

    def dimensionAggregate(self, colname, valcol, aggfunc=sum, chunksize=1000000, use_dict={}, defaultval=0):
        numchunks = 0

        groupdict = use_dict

        response = self.store.select(self.tablename, chunksize=chunksize)
        for chunk in response:
            grouped = chunk.groupby(colname)
            aggregated = grouped.aggregate(aggfunc)
            
            for row in aggregated.iterrows():
                mykey = row[0]
#                print >>sys.stderr, "mykey is %s" % mykey
#                sys.exit(-1)
                myval = row[1][valcol]
                if mykey in groupdict:
                    groupdict[mykey] = aggfunc([groupdict[mykey], myval])
                else:
                    groupdict[mykey] = myval

            numchunks += chunksize
            print >>sys.stderr, "%d completed." % numchunks

        resultdf = pd.DataFrame.from_dict(groupdict, orient="index")
        resultdf.reset_index(level=0, inplace=True)
        resultdf.columns = [colname, valcol]
        return resultdf

    def reprocess(self, newfilename, dffunc, indexcols, min_itemsizes, chunksize=1000000):
        store = pd.HDFStore(newfilename, "w", complevel=9, complib="blosc")

        numchunks = 0
        for chunk in self.store.select(self.tablename, chunksize=chunksize):
            newchunk = dffunc(chunk)
            store.append("tensor", newchunk, data_columns=indexcols, nan_rep="_!NaN_", min_itemsize=min_itemsizes)
            numchunks += chunksize
            print >>sys.stderr, "%d completed." % numchunks

        return Tensor(store, "tensor")

    # def groupAggregateDimension(self, colname, valcol, aggfunc=sum, chunksize=1000000, groupblocksize=50000, use_dict={}, defaultval=0):
    #     """
    #     The chunksize only controls how much is loaded, the aggregation returns the full group listing.
    #     """

    #     groupdict = use_dict
        
    #     groups = self.uniqueDimension(colname, chunksize=chunksize)
    #     size = 0
    #     for block in chunks(list(groups), groupblocksize):
    #         fixedblock = ["'" + x + "'" for x in block if "\"" not in x]
    #         item = "[" + ",".join(fixedblock) + "]"
    #         print >>sys.stderr, "Working on new block from %d." % size
    #         size += len(block)
    #         response = self.store.select(self.tablename, where=("%s=%s" % (colname, item)), chunksize=chunksize)
    #         for chunk in response:
    #             grouped = chunk.groupby(colname)
    #             aggregated = grouped.aggregate(aggfunc)

    #             for row in aggregated.index:
    #                 if row in groupdict:
    #                     groupdict[row] = aggfunc([groupdict[row], aggregated.ix[row][valcol]])
    #                 else:
    #                     groupdict[row] = aggregation.ix[row][valcol]
    #             del chunk
    #             del grouped
    #             del aggregated
    #             gc.collect()

    #         for row in block:
    #             if not row in groupdict:
    #                 groupdict[row] = defaultval

    #         del response
    #         gc.collect()

    #     return groupdict

    def close(self):
        self.store.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

class LengthStore:
    """When you have a list of lengths as a DF.  Expects a single string
    column for the 'title' of the vector."""
    def __init__(self, store, tablename, vecnamecol, lengthcol):
        if isinstance(store, pd.HDFStore):
            self.store = store
        else:
            self.store = pd.HDFStore(store, "r")

        self.tablename = tablename
        self.vecnamecol = vecnamecol
        self.lengthcol = lengthcol

    def getLengths(self, lengths):
        lengthquery = pd.Term(self.vecnamecol, "=", lengths)
        return self.store.select(self.tablename, where=lengthquery).set_index(self.vecnamecol)

    def close(self):
        self.store.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

class Matricisation:
    """Use when you've matricized the tensor into HDFStore hashes."""

    def __init__(self, storesdict):
        self.stores = {}
        for key in storesdict:
            if isinstance(storesdict[key], pd.HDFStore):
                self.stores[key] = storesdict[key]
            else:
                self.stores[key] = pd.HDFStore(storesdict[key], "r")

        self.indices = {}

    def getMemberVectors(self, target, targetcol, membercol, criteria={}, topN=20, labelconverter=None, wordfilter=lambda x: True):
        """Get the pre-centroid vectors from the matricized tensor. The 'target' is the thing you want the centroid for. 
        The 'targetcol' is the name of the column (should be a matrix store already registered with the constructor).
        The 'membercol' is the place where you want to look up the 'members' of the centroid.
        The 'lengthstore' is a LengthStore as above and provides the lengths as a DataFrame.
        The 'lengthcol' is the name of the length column in the DataFrame.
        The 'criteria' is a filtering criterion over MultiIndex columns.
        The 'topN' is how many 'members' the centroid should have.
        The 'labelconverter' turns MultiIndex axis labels into something that can be used to query the 'lengthstore'."""      
        
        # get the top members.
        topmembers = self.getMemberList(target, targetcol, membercol, criteria, topN, labelconverter, wordfilter)

        # collect the vectors for the top members.
        membervectors = []
        for x in topmembers:
            try:
                v = self.stores[membercol][x][x]
                # v = v / np.sqrt(np.square(v).sum())
                membervectors.append(v)
            except KeyError:
                print >>sys.stderr, "missing", x, "in column for", target
        #membertable = reduce(lambda x, y: x.join(y, how="outer"), membervectors[1:], membervectors[0])
        
        return (membervectors, topmembers)

    def getMemberList(self, target, targetcol, membercol, criteria={}, topN=20, labelconverter=None, wordfilter=lambda x: True):
        """Get the pre-centroid word list from the matricized tensor. Only return the list of words.
        Modifier: Tony Hong
        The 'target' is the thing you want the centroid for. 
        The 'targetcol' is the name of the column (should be a matrix store already registered with the constructor).
        The 'membercol' is the place where you want to look up the 'members' of the centroid.
        The 'lengthstore' is a LengthStore as above and provides the lengths as a DataFrame.
        The 'lengthcol' is the name of the length column in the DataFrame.
        The 'criteria' is a filtering criterion over MultiIndex columns.
        The 'topN' is how many 'members' the centroid should have.
        The 'labelconverter' turns MultiIndex axis labels into something that can be used to query the 'lengthstore'."""
        
        # get the matrix
        cache = self.stores[targetcol]
        try:
            targetrows = cache[target]
            targetspace = targetrows
        except KeyError:
            return pd.DataFrame().sum()
        
        # cut it down to the rows we want.
        for key in criteria:
            if isinstance(criteria[key], list):
                try:
                    targetrows = pd.concat([targetrows.xs(x, level=key) for x in criteria[key]])
                except KeyError:
                    return pd.DataFrame().sum()
            else:
                targetrows = targetrows(criteria[key], level=key)

        #print >>sys.stderr, criteria, targetrows[:20]

        #rowlabels = targetrows.index.tolist()
        #if labelconverter:
        #    rowlabels = [labelconverter(x) for x in rowlabels]

        #relevantrows = target[targetspace.index.get_level_values(membercol).isin(rowlabels)]
        relevantgroups = targetrows.groupby(level=membercol)
        
        relevantnorms = relevantgroups.apply(nla.norm)

        # FIXED: sort function is deprecated
        # relevantnorms.sort(ascending=False)
        # Hint: FutureWarning: sort is deprecated, use sort_values(inplace=True) for INPLACE sorting
        relevantnorms.sort_values(inplace=True, ascending=False)
        
        # get the top members.
        topmembers = [x for x in relevantnorms.index.tolist() if wordfilter(x)][:topN]

        return topmembers

    def getCentroid(self, target, targetcol, membercol, criteria={}, topN=20, labelconverter=None, wordfilter=lambda x: True):
        """Get the centroid from the matricized tensor. The 'target' is the thing you want the centroid for. 
        The 'targetcol' is the name of the column (should be a matrix store already registered with the constructor).
        The 'membercol' is the place where you want to look up the 'members' of the centroid.
        The 'lengthstore' is a LengthStore as above and provides the lengths as a DataFrame.
        The 'lengthcol' is the name of the length column in the DataFrame.
        The 'criteria' is a filtering criterion over MultiIndex columns.
        The 'topN' is how many 'members' the centroid should have.
        The 'labelconverter' turns MultiIndex axis labels into something that can be used to query the 'lengthstore'."""

        membervectors = self.getMemberVectors(target, targetcol, membercol, criteria, topN, labelconverter, wordfilter=wordfilter)

        # TODO: not normalized, should be
        # transpose the new matrix and sum the columns. This is the centroid.
        return pd.concat(membervectors[0]).sum(level=[0,1])

    def getCentroidLMIRank(self, target, targetcol, membercol, criteria={}, topN=20):
        """Get the centroid from the matricized tensor. The 'target' is the thing you want the centroid for. 
        The 'targetcol' is the name of the column (should be a matrix store already registered with the constructor).
        The 'membercol' is the place where you want to look up the 'members' of the centroid.
        The 'criteria' is a filtering criterion over MultiIndex columns.
        The 'topN' is how many 'members' the centroid should have.
        """
        
        # get the matrix
        cache = self.stores[targetcol]
        try:
            targetrows = cache[target]
        except KeyError:
            return pd.DataFrame().sum()
        
        # cut it down to the rows we want.
        for key in criteria:
            if isinstance(criteria[key], list):
                targetrows = pd.concat([targetrows.xs(x, level=key) for x in criteria[key]])
            else:
                targetrows = targetrows(criteria[key], level=key)

        sortedrows = targetrows.sort(target, ascending=False)
        
        # get the top members.
        topmembers = sortedrows[:topN].index.tolist()

        # collect the vectors for the top members.
        membervectors = [self.stores[membercol][x] for x in topmembers]

        # join the vectors into a single table.
        membertable = reduce(lambda x, y: x.join(y, how="outer"), membervectors[1:], membervectors[0])

        # transpose the new matrix and sum the columns. This is the centroid.
        return membertable.T.sum()


    def getRow(self, rowname, rowval):
        """Returns a single row from one of the matricisations."""
        cache = self.stores[rowname]
        try:
            v = cache[rowval].T.sum()
            # v = v / np.sqrt(np.square(v).sum())
            return v
        except KeyError:
            return pd.DataFrame().sum()

    def close(self):
        for key in self.stores:
            self.stores[key].close()

    def loadIndex(self, axis):
        if axis not in self.indices:
            self.indices[axis] = self.stores[axis].keys()

    def mapItems(self, axis, func):
        self.loadIndex(axis)

        resultlist = []
        for item in self.indices[axis]:
            resultlist.append((item, func(self.stores[axis][item])))

        return pd.DataFrame(resultlist)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()


    
