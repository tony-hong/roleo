'''
    myio.py
    @author: Tony Hong
'''

import os
import pickle


def read_file(path):
    '''
    read raw text from file
    '''
    raw_text = open(path, 'r').read().decode('utf-8')
    return raw_text

def read_pcl_file(path):
    '''
    read from pcl file
    '''
    f = open(path, 'r')
    result = pickle.load(f)
    return result

def get_file_dict(container, file_dir, sp_filetype=''):
    result = dict()
    if type(container) == type({}):
        filenames = container.itervalues()
    elif type(container) == type([]):
        filenames = container
    else:
        return result

    if sp_filetype:
        suffix = '.' + sp_filetype
    else:
        suffix = ''

    for k in filenames:
        names = k.split('.')
        name = names[0]
        if suffix:
            result[name] = os.path.join(file_dir, name + suffix)
        else:
            result[name] = os.path.join(file_dir, k)

    return result

def get_text_dict(file_dict):
    '''
    set up text dict from file dict
    '''
    result = dict()
    for k, v in file_dict.iteritems():
        result[k] = read_file(v)
    return result

def get_pcl_dict(file_dict):
    '''
    set up text dict from pcl file dict
    '''
    result = dict()
    for k, v in file_dict.iteritems():
        result[k] = read_pcl_file(v)
    return result
