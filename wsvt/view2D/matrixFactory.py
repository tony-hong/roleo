'''
    matrixFactory.py
'''
import os
import sys

# Configuration of environment
sys.path.append('Rollenverteilung/src/lib')
os.system('export LD_LIBRARY_PATH=hdf5/1.8.16/lib')

from rv.structure.Tensor import Matricisation

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

MODEL_MAPPING = {
    'SDDM'      :   ['wackylmi-malt-v2-36K.word0.h5', 'wackylmi-malt-v2-36K.word1.h5'],
    'TypeDM'    :   ['typedm.matricised.word0.h5'   , 'typedm.matricised.word1.h5'],
    'RBE'       :   ['wackylmi-malt-v2-36K.word0.h5', 'wackylmi-malt-v2-36K.word1.h5'],
}

class MatrixFactory:
    def __init__(self):
        self.matrixMapping = {}
        for n in MODEL_MAPPING.keys():
            self.matrixMapping[n] = Matricisation({
                'word0' : os.path.join(DATA_DIR, MODEL_MAPPING[n][0]),
                'word1' : os.path.join(DATA_DIR, MODEL_MAPPING[n][1]) 
            })
        self.currentModel = 'SDDM'

    def getMatrix(self, modelName):
        return self.matrixMapping[modelName]

    def getCurrentModel(self):
        return self.currentModel

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        for n in MODEL_MAPPING.keys():
            self.matrixMapping[n].close()
