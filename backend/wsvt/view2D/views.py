import json
import re

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader

from models import SemanticRole
from dataProcess import *
from errorCodeJSON import errorCodeJSON as ecj

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
    result = {}

    print 'v: ' + verb
    print 'r: ' + role
    print 'n: ' + noun
    print 'group: ' + group

    if group not in ['noun', 'verb']:
        result = {'errCode' : errorCode.INTERNAL_ERROR}
    else:
        nre = re.match(r'^[a-z]+$', noun)
        vre = re.match(r'^[a-z]+$', verb)
        if not nre:
            result = {'errCode' : errorCode.NOUN_FORMAT_ERROR}
        elif not vre:
            result = {'errCode' : errorCode.VERB_FORMAT_ERROR}
        else:
            result = process(verb, noun, role, group)

    return JsonResponse(result)

def errorCodeJSON(request):
    return JsonResponse(ecj, safe = False)
