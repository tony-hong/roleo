'''
    embeddingFactory.py
'''

import os
import sys
import pickle

import myio


# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

RBE_DIR = os.path.join(DATA_DIR, 'Siemawe')
W2V_PATH = os.path.join(DATA_DIR, 'GoogleNews-vectors-negative300.pcl')

class EmbeddingFactory:
    def __init__(self):
        file_list = os.listdir(RBE_DIR)
        file_dict = myio.get_file_dict(file_list, RBE_DIR)
        
        self.RBE_dict = myio.get_pcl_dict(file_dict)

        with open(W2V_PATH, 'r') as f: 
            self.W2V_embedding = pickle.load(f)

        self.W2V_dict = dict()
        
        for k in file_dict.keys():
            self.W2V_dict[k] = self.W2V_embedding

        self.embedding_mapping = {
            'RBE'   :   self.RBE_dict,
            'W2V'   :   self.W2V_dict
        }

    def getEmbeddingFromKey(self, key):
        return self.RBE_dict.get(key, -1)

    def getVocabulary(self):
        return self.RBE_dict.get('vocabulary', -1)

    def getEmbedding(self, model):
        return self.embedding_mapping[model]

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        pass
   