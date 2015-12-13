import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader

from models import SemanticRole
from dataProcess import *


'''
import os
import math
import pandas as pd

from rv.structure.Tensor import Matricisation
from rv.similarity.Similarity import cosine_sim

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
'''


def index(request):
    
    template = loader.get_template('view2D/index.html')
    role_list = SemanticRole.objects.all()
    response = { 'role_list' : role_list }

    context = RequestContext(request, response)

    return HttpResponse(template.render(context))

def query(request):
    verb = request.POST['verb'] + '-v'
    role = request.POST['role']
    noun = request.POST['noun'] + '-n'

    if not (verb and noun):
        print 'one word is empty'
    print 'v: ' + verb
    print 'r: ' + role
    print 'n: ' + noun

    # logic = Logic()
    result = process(verb, role, noun)

    # template = loader.get_template('view2D/index.html')
    # role_list = SemanticRole.objects.all()

    # result = json.dumps(result)
    # response = {
    #     'role_list' : role_list, 
    #     'data' : result, 
    # }
    # context = RequestContext(request, response)

    return JsonResponse(result)

