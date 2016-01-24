from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader

from models import SemanticRole
from dataProcess import process

from errorCodeJSON import errorCodeJSON as ecj
from validator import validate


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

    query0 = ''
    query1 = ''
    semanticRole = role
    result = {}

    print 'v: ' + verb
    print 'r: ' + role
    print 'n: ' + noun
    print 'group: ' + group
    print 'top_results: ' + str(topN)

    double = True
    if not noun or not verb:
        double = False

    isValid, errorMessage = validate(verb, noun, group)

    if isValid:
        pass
    else:
        result = errorMessage
        return JsonResponse(result)        

    if group == 'noun':
        query0 = noun + '-n'
        semanticRole = semanticRole + '-1'
        if not verb:
            query1 = verb + '-v'
    elif group == 'verb':
        query0 = verb + '-v'
        if not noun:
            query1 = noun + '-n'
    else:        
        print 'exception: internal error!'
        result = {'errCode' : errorCode.INTERNAL_ERROR}
        return JsonResponse(result)

    
    result = process(query0, query1, semanticRole, double, topN)
    return JsonResponse(result)

def errorCodeJSON(request):
    return JsonResponse(ecj, safe = False)
