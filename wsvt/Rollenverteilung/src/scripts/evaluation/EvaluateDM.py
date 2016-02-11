#!/usr/bin/env python

import sys
import os
from argparse import ArgumentParser
import pandas as pd
import string
import random
import multiprocessing as mp
import traceback

# to divide up the input file into iterators.
def grouping(seq, n):
    x = 0
    q = []
    for i in seq:
        if x == n:
            yield q
            x = 1
            q = [i]
        else:
            x = x + 1
            q.append(i)
    if q:
        yield q

if __name__ == "__main__":
    parser = ArgumentParser(description="Produce cosines from a DM based on role data.")
    parser.add_argument('word0filename', metavar='word0.h5', type=str, help='The word0 matricization')
    parser.add_argument('word1filename', metavar='word1.h5', type=str, help='The word1 matricization')
    parser.add_argument('mappingfilename', metavar='mapping.py', type=str, help='The mapping eval script for role conversion')
    parser.add_argument('evalfilename', metavar='evaldata', type=str, help='The evaluation file in columns')
    parser.add_argument('resultfilename', metavar='resultfile', type=str, help='The name of the output file to create (if multiprocessing, the prefix)')
    parser.add_argument('-p', '--processors', type=int, default=1, help='The number of processors to allocate to the task')
    parser.add_argument('-c', '--chunksize', type=int, default=1, help='The size of the chunk per processor')

    args = parser.parse_args()

    evalfile = open(args.evalfilename, "r")
    mappingfile = open(args.mappingfilename, "r")
    mappingtext = mappingfile.readlines()
    mapping = eval(" ".join(mappingtext))

    def worker(lines):
        print >>sys.stderr, "Worker started with", len(lines), "lines"
        print >>sys.stderr, lines
        resultfilename = args.resultfilename
        if args.processors > 1:
            resultfilename = resultfilename + "." + ''.join(random.choice(string.ascii_lowercase) for i in range(8))
        resultfile = open(resultfilename, "w")
        results = []
        verbcache = {}

        from rv.structure.Tensor import Matricisation
        from rv.similarity.Similarity import cosine_sim

        matricisation = Matricisation({'word0':args.word0filename, 'word1':args.word1filename})


        for line in lines:
            print >>sys.stderr, "trying line", line
            words = line.split()
            verb = words[0]
            link = words[2]
            try:
                filler = matricisation.getRow('word0', words[1])
            except e:
                print >>sys.stderr, "filler", words[1], "failed with:"
                traceback.print_exc(None, sys.stderr)
                continue

            print >>sys.stderr, "got filler", filler
            
            #check to see if the combination is in the verbcache.
            verbrole = ("%s-%s" % (verb, link))
            print >>sys.stderr, "Checking for", verbrole
            if verbrole not in verbcache:
                print >>sys.stderr, "it's not there yet"
                try:
                    verbcache[verbrole] = matricisation.getCentroid(verb, 'word1', 'word0', {'link':mapping[link]}, wordfilter=lambda x: x[-2:] != '-v')
                except IndexError:
                    print >>sys.stderr, "Oops! IndexError on", verbrole
                    continue
                except e:
                    print >>sys.stderr, "verbrole", verbrole, "failed with:"
                    traceback.print_exc(None, sys.stderr)
                    continue
                print >>sys.stderr, "Added verbrole", verbrole, verbcache[verbrole]
            
            centroid = verbcache[verbrole]
            try:
                result = cosine_sim(centroid, filler)
            except e:
                print >>sys.stderr, "verbrole/filler", verbrole, words[1], "failed with:"
                traceback.print_exc(None, sys.stderr)
                continue

            resultstr = "%s\t%s" % ("\t".join(words), str(result))
            results.append(resultstr)
            resultfile.write("%s\n" % (resultstr))
        
        resultfile.close()
        matricisation.close()
    
        return results

    pool = mp.Pool(args.processors)
    print >>sys.stderr, "Starting workers."
    allresults = pool.map_async(worker, grouping(evalfile, args.chunksize))
    pool.close()
    pool.join()
    print type(allresults.get())

    evalfile.close()

