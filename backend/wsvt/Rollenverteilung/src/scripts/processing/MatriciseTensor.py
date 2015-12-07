#!/usr/bin/env python

import os
import sys
import pandas as pd
import warnings
import tables
from rv.structure.Tensor import Tensor

warnings.filterwarnings('ignore',category=pd.io.pytables.PerformanceWarning)
warnings.filterwarnings('ignore',category=tables.NaturalNameWarning)

if len(sys.argv) < 5:
    print >>sys.stderr, "MatriciseTensor.py infile.h5 outfile.h5 axisname valcol"
    sys.exit(-1)

infile = pd.HDFStore(sys.argv[1], mode="r")
outfile = pd.HDFStore(sys.argv[2], mode="w", complevel=1, complib="blosc")
axis = sys.argv[3]
valcol = sys.argv[4]

print >>sys.stderr, "Getting axis items."
itemstensor = Tensor(infile, "tensor")
#items = infile.select("tensor", where=("columns=%s" % axis))
print >>sys.stderr, "Uniquing"
uniqued = itemstensor.uniqueDimension(axis)
print >>sys.stderr, "There are", len(uniqued), "unique items."

othercols = [x for x in infile.get_storer("tensor").data_columns if x not in [axis, valcol]]

count = 0
for item in uniqued:
    item = item.replace("\"", "\\\"")
    if item[0] == "_":
        print >>sys.stderr, "Skipping underscore item", item
        continue

    itemdf = infile.select("tensor", where=("%s=%s" % (axis, item)))
    itemdf = itemdf.set_index(othercols)
    itemdf = itemdf[[valcol]]
    itemdf.columns = [item]
    outfile[item] = itemdf

    if count % 100 == 0:
        print >>sys.stderr, "Count is %d." % count
    count = count + 1

print >>sys.stderr, "Done."

outfile.close()
infile.close()
