'''
    Command initiation tool for WSVT
    Copy-paste these code into python shell
'''

import os
import math
import sys
import re

sys.path.append('Rollenverteilung/src/lib')
os.system('export LD_LIBRARY_PATH=hdf5/1.8.16/lib')

import matplotlib.pyplot as plt
import pandas as pd

from rv.structure.Tensor import Matricisation
from rv.similarity.Similarity import cosine_sim

import errorCode

matrix = Matricisation({
    'word0' : 'view2D/wackylmi-malt-v2-36K.word0.h5',
    'word1' : 'view2D/wackylmi-malt-v2-36K.word1.h5'
})