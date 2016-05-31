'''
    embeddingFactory.py
'''

import os
import sys

import myio

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EMBEDDING_DIR = os.path.join(DATA_DIR, 'Siemawe')


class EmbeddingFactory:
    def __init__(self):
        file_list = os.listdir(EMBEDDING_DIR)
        file_dict = myio.get_file_dict(file_list, EMBEDDING_DIR)
        self.embedding_dict = myio.get_pcl_dict(file_dict)

    def getEmbeddingFromKey(self, key):
        return self.embedding_dict.get(key, -1)

    def getVocabulary(self):
        return self.embedding_dict.get('vocabulary', -1)

    def getEmbedding(self):
        return self.embedding_dict

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        for n in MODEL_MAPPING.keys():
            self.matrixMapping[n].close()
