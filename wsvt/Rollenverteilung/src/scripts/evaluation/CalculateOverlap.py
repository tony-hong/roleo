#!/usr/bin/env python

import os
import sys
from argparse import ArgumentParser
import pandas as pd
from rv.structure.Tensor import Matricisation

def compute_jaccard_index(set_1, set_2):
    n = len(set_1.intersection(set_2))
    return n / float(len(set_1) + len(set_2) - n) 

if __name__ == "__main__":
    parser = ArgumentParser(description="Measure the overlap (Jaccard index) between the candidate members of centroids across two tensors.")
    parser.add_argument('word1afilename', metavar='word1a.h5', type=str, help='The word1 matricization on the left side of the comparison')
    parser.add_argument('word1bfilename', metavar='word1b.h5', type=str, help='The word1 matricization on the right side of the comparison')
    parser.add_argument('mappingafilename', metavar='mappinga.py', type=str, help='The mapping eval script for left-side role conversion')
    parser.add_argument('mappingbfilename', metavar='mappingb.py', type=str, help='The mapping eval script for right-side role conversion')
    parser.add_argument('evalfilename', metavar='evaldata', type=str, help='The evaluation file in columns')
    parser.add_argument('-r', '--role', type=str, default=None, help='A role to filter by.')

    args = parser.parse_args()

    evaldata = pd.read_table(args.evalfilename, header=None)
    evaldata = evaldata[[0,2]].sort().drop_duplicates()
    if args.role:
        evaldata = evaldata[evaldata[2] == args.role]

    mappingafile = open(args.mappingafilename, "r")
    mappingatext = mappingafile.readlines()
    mappinga = eval(" ".join(mappingatext))

    mappingbfile = open(args.mappingbfilename, "r")
    mappingbtext = mappingbfile.readlines()
    mappingb = eval(" ".join(mappingbtext))

    matricisationa = Matricisation({'word1':args.word1afilename})
    matricisationb = Matricisation({'word1':args.word1bfilename})

    jaccards = []
    for (index, verb, role) in evaldata.itertuples():
        print "Verb = ", verb, "; Role = ", role
        try:
            responsea = matricisationa.getMemberVectors(verb, 'word1', 'word0', {'link':mappinga[role]})
            #print responsea
            (membersa, topsa) = responsea
            (membersb, topsb) = matricisationb.getMemberVectors(verb, 'word1', 'word0', {'link':mappingb[role]})

            print "From ", args.word1afilename, ":"
            print str(sorted(topsa))
            print "From ", args.word1bfilename, ":"
            print str(sorted(topsb))
        
            jaccard = compute_jaccard_index(set(topsa), set(topsb))
            jaccards.append(jaccard)

            print "Jaccard index = ", jaccard
        except KeyError:
            print "Role not found for one of the items. Skipping."
        except ValueError:
            print "One of the verb lookups failed. Possibly check mapping."

        print "***"


    print "Number of items processed = ", len(jaccards)
    print "Average jaccard index = ", sum(jaccards)/float(len(jaccards))
