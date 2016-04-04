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

role_mapping = dict()

def index(request):
    template = loader.get_template('view2D/index.html')

    # Obtain objects of SemanticRole from models 
    # role_list = SemanticRole.objects.all()
    # response = { 'role_list' : role_list }

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

def roleDictJSON(request):
    # Obtain objects of SemanticRole from models 
    role_list_SDDM = list()
    role_list_TypeDM = list()
    role_list_TypeDM_split = list()

    role_list = SemanticRole.objects.exclude(
        modelSupport = 3
    )
    for r in role_list:
        role_list_SDDM.append({
            'label'   :   r.labelSDDM,
            'name'    :   r.name
        })
    response = { 'SDDM' : role_list_SDDM }
    
    role_list = SemanticRole.objects.exclude(
        modelSupport = 1
    )
    for r in role_list:
        role_list_TypeDM.append({
            'label'   :   r.labelTypeDM,
            'name'    :   r.name
        })
        role_list_TypeDM_split.append({
            'label'   :   r.labelTypeDM.split(','),
            'name'    :   r.name
        })
    response['TypeDM'] = role_list_TypeDM

    role_mapping = {
        'SDDM'      :   role_list_SDDM,
        'TypeDM'    :   role_list_TypeDM_split
    }

    return JsonResponse(response, safe = False)


'''
    This call of the index.html in the case that the "Change Model" button is clicked
    Later here the new model should be loaded.
'''
def changeModel(request): 
    template = loader.get_template('view2D/index.html')
    # Obtain attributes from request
    model = request.GET['select_model']
    mf.setModel(model)
    context = RequestContext(request)

    return HttpResponse(template.render(context))
