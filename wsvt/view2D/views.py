'''
    This module is all views in view2D app.
    It is acting like a controller(in MVC) in Django.

    @Author: 
        Tony Hong
'''
import logging

from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader

from models import SemanticRole
from matrixFactory import MatrixFactory
from dataProcess import process, mf

from errorCodeJSON import errorCodeJSON as ecj
from validator import validate

logger = logging.getLogger('django')

def index(request):
    template = loader.get_template('view2D/index.html')

    # Obtain objects of SemanticRole from models 
    role_list = SemanticRole.objects.all()
    response = { 'role_list' : role_list }

    context = RequestContext(request, response)

    return HttpResponse(template.render(context))

def help(request):
    template = loader.get_template('view2D/help.html')

    return HttpResponse(template.render())

def contact(request):
    template = loader.get_template('view2D/contact.html')

    return HttpResponse(template.render())

def impressum(request):
    template = loader.get_template('view2D/impressum.html')

    return HttpResponse(template.render())

def query(request):
    # Obtain attributes from request
    verb = request.POST['verb'].strip().lower()
    semanticRole = request.POST['role']
    noun = request.POST['noun'].strip().lower()
    group = request.POST['group1']
    topN = int(request.POST['top_results'])

    result = {}
    
    # LOG
    logger.debug('v: %s' , verb)
    logger.debug('r: %s' , semanticRole)
    logger.debug('n: %s' , noun)
    logger.debug('group: %s' , group)
    logger.debug('top_results: %d' , topN)

    # Perform validation on request attributes
    isValid, errorMessage = validate(verb, noun, group, topN)

    if isValid:
        result = process(verb, noun, semanticRole, group, topN)
    else:
        result = errorMessage
    
    return JsonResponse(result)

def errorCodeJSON(request):
    return JsonResponse(ecj, safe = False)

# def roleList(request):
#     # Obtain objects of SemanticRole from models 
#     role_list = SemanticRole.objects.all()
#     response = { 'role_list' : role_list }
#     return JsonResponse(response, safe = False)

'''
    This call of the index.html in the case that the "Change Model" button is clicked
    Later here the new model should be loaded.
'''
def changeModel(request): 
    # Obtain attributes from request
    verb = request.POST['verb'].strip().lower()
    semanticRole = request.POST['role']
    noun = request.POST['noun'].strip().lower()
    group = request.POST['group1']
    topN = int(request.POST['top_results'])
    model = request.POST['select_model']

    result = {}
    
    # LOG
    logger.debug('v: %s' , verb)
    logger.debug('r: %s' , semanticRole)
    logger.debug('n: %s' , noun)
    logger.debug('group: %s' , group)
    logger.debug('top_results: %d' , topN)

    # Perform validation on request attributes
    isValid, errorMessage = validate(verb, noun, group, topN)

    if isValid:
        mf.setModel(model)
        result = process(verb, noun, semanticRole, group, topN)
    else:
        result = errorMessage
    
    return JsonResponse(result)
