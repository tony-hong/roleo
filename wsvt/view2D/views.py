'''
    This module is all views in view2D app.
    It is acting like a controller(in MVC) in Django.

    @Author: 
        Tony Hong
'''
import logging

from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader

from matrixFactory import MatrixFactory
from dataProcess import process, mf
from roleDict import getRoleDict

import errorCode
from errorCodeJSON import errorCodeJSON as ecj
from validator import validate

logger = logging.getLogger('django')


def index(request):
    template = loader.get_template('view2D/index.html')
    context = RequestContext(request)

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
    verb = str(request.POST['verb']).strip().lower()
    semanticRole = str(request.POST['role'])
    noun = str(request.POST['noun']).strip().lower()
    group = str(request.POST['group1'])
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

def roleDictJSON(request):
    # Obtain objects of SemanticRole from models 
    response = getRoleDict()

    return JsonResponse(response, safe = False)


'''
    This call of the index.html in the case that the "Change Model" button is clicked
    Later here the new model should be loaded.
'''
def changeModel(request): 
    template = loader.get_template('view2D/index.html')
    # Obtain attributes from request
    model = request.GET['select_model']
    if(mf.setModel(model)):
        print 'Change model successfully'
        response = {}
    else:
        logger.critical( 'errCode: %d. internal error!', errorCode.INTERNAL_ERROR)
        response = {'errCode' : errorCode.INTERNAL_ERROR}
    context = RequestContext(request, response)

    return HttpResponse(template.render(context))
