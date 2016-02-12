import logging

from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader

from models import SemanticRole
from dataProcess import process

from errorCodeJSON import errorCodeJSON as ecj
from validator import validate

logger = logging.getLogger('django')

def index(request):
    template = loader.get_template('view2D/index.html')
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
    verb = request.POST['verb'].strip().lower()
    role = request.POST['role']
    noun = request.POST['noun'].strip().lower()
    group = request.POST['group1']
    topN = int(request.POST['top_results'])

    semanticRole = role
    result = {}
    
    # LOG
    logger.debug('v: %s' , verb)
    logger.debug('r: %s' , role)
    logger.debug('n: %s' , noun)
    logger.debug('group: %s' , group)
    logger.debug('top_results: %d' , topN)

    isValid, errorMessage = validate(verb, noun, group)

    if isValid:
        result = process(verb, noun, semanticRole, group, topN)
    else:
        result = errorMessage
    
    return JsonResponse(result)

def errorCodeJSON(request):
    return JsonResponse(ecj, safe = False)
