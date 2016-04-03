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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_MAPPING = {
    'SDDMX'     :   ['wackylmi-malt-v2-36K.word0.h5', 'wackylmi-malt-v2-36K.word1.h5'],
    'TypeDM'    :   ['typedm.matricised.word0.h5'   , 'typedm.matricised.word1.h5']
}

class MatrixFactory:
    def __init__(self):
        self.matrix = Matricisation({
            'word0' : os.path.join(BASE_DIR, MODEL_MAPPING['SDDMX'][0]),
            'word1' : os.path.join(BASE_DIR, MODEL_MAPPING['SDDMX'][1]) 
        })

    def setModel(self, modelName):
        if modelName in MODEL_MAPPING.keys():
            fileNameList = MODEL_MAPPING[modelName]
        else:
            logger.critical( 'errCode: %d. internal error!', errorCode.INTERNAL_ERROR)
            result = {'errCode' : errorCode.INTERNAL_ERROR}
            return False
        self.matrix.close()
        self.matrix = Matricisation({
            'word0' : os.path.join(BASE_DIR, fileNameList[0]),
            'word1' : os.path.join(BASE_DIR, fileNameList[1]) 
        })
        return True

    def getMatrix(self):
        return self.matrix

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.matrix.close()
