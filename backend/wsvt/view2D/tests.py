#-*- coding:utf-8 -*-

from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest

from view2D.views import index, query, help, contact, impressum
from view2D.dataProcess import process

import view2D.errorCode as errorCode


class IndexTest(TestCase):
    def test_view2D_URL_ResolvesTo_IndexView(self):
        found = resolve('/view2D/')
        self.assertEqual(found.func, index)

class helpTest(TestCase):
    def test_help_URL_ResolvesTo_HelpView(self):
        found = resolve('/view2D/help/')
        self.assertEqual(found.func, help)

class ContactTest(TestCase):
    def test_contact_URL_ResolvesTO_ContactView(self):
        found = resolve('/view2D/contact/')
        self.assertEqual(found.func, contact)

class ImpressumTest(TestCase):
    def test_Impressum_URL_ResolvesTo_ImpressumView(self):
       found = resolve('/view2D/impressum/')
       self.assertEqual(found.func, impressum)
        

class QueryTest(TestCase):
    def test_NOUN_FORMAT_ERROR(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['verb'] = 'eat'
        request.POST['role'] = 'A0'
        request.POST['noun'] = '你好'.decode('utf8')
        request.POST['group1'] = 'verb'
        request.POST['top_results'] = 20
        response = query(request)
        realResult = response.content

        result = '{"errCode": ' + str(errorCode.NOUN_FORMAT_ERROR) + '}'
        self.assertEqual(result, realResult)
    
    def test_VERB_FORMAT_ERROR(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['verb'] = '你好'.decode('utf8')
        request.POST['role'] = 'A0'
        request.POST['noun'] = 'apple'
        request.POST['group1'] = 'verb'
        request.POST['top_results'] = 20
        response = query(request)
        realResult = response.content

        result = '{"errCode": ' + str(errorCode.VERB_FORMAT_ERROR) + '}'
        self.assertEqual(result, realResult)
    
    def test_group_notExist(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['verb'] = 'eat'
        request.POST['role'] = 'A0'
        request.POST['noun'] = 'apple'
        request.POST['group1'] = 'asdf'
        request.POST['top_results'] = 20
        response = query(request)
        realResult = response.content

        result = '{"errCode": ' + str(errorCode.INTERNAL_ERROR) + '}'
        self.assertEqual(result, realResult)

    def test_NOUN_EMPTY(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['verb'] = 'eat'
        request.POST['role'] = 'A0'
        request.POST['noun'] = ''
        request.POST['group1'] = 'noun'
        request.POST['top_results'] = 20
        response = query(request)
        realResult = response.content

        result = '{"errCode": ' + str(errorCode.NOUN_EMPTY) + '}'
        self.assertEqual(result, realResult)

    def test_VERB_EMPTY(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['verb'] = ''
        request.POST['role'] = 'A0'
        request.POST['noun'] = 'apple'
        request.POST['group1'] = 'verb'
        request.POST['top_results'] = 20
        response = query(request)
        realResult = response.content

        result = '{"errCode": ' + str(errorCode.VERB_EMPTY) + '}'
        self.assertEqual(result, realResult)

																												

class DataProcessorTest(TestCase):
    def test_process(self):
        realResult = process('eat-v', 'apple-n', 'A0', True, 20)
        queryDict = {
            'y': 0.7788627028935319, 
            'x': 0.45877782991981186, 
            'cos': 0.096960180200616961, 
            'word': 'apple-n'
        }
        wordList = ['announce-v', 'release-v', 'launch-v', 'unveil-v', 'have-v', 'make-v', 'say-v', 'introduce-v', 'sell-v', 'add-v', 'do-v', 'recommend-v', 'admit-v', 'claim-v', 'listen-v', 'offer-v', 'recall-v', 'dominate-v', 'slice-v', 'decide-v']
        self.assertEqual('apple-n', realResult['queried']['word'])

        wordAppeared = True
        nodes = realResult['nodes']
        for w in wordList:
            if w in nodes:
                wordAppeared = False
        self.assertEqual(True, wordAppeared)

    def test_processTop100(self):
	realResult = process('study-v', 'adult-n', 'A0', True, 100)
        wordList = ['he-n', 'i-n', 'researcher-n', 'pupil-n', 'scientist-n', 'class-n', 'university-n', 'group-n', 'project-n', 'scholarship-n', 'team-n', 'astronomer-n', 'candidate-n', 'psychologist-n', 'paper-n', 'scholar-n', 'anthropologist-n', 'author-n', 'learner-n', 'fellowship-n', 'historian-n', 'david-n', 'andrew-n', 'module-n', 'child-n', 'biologist-n', 'film-n', 'undergraduate-n', 'sociologist-n', 'research-n', 'london-n', 'john-n', 'archaeologist-n', 'uk-n', 'objective-n', 'participant-n', 'science-n', 'spectroscopy-n', 'us-n', 'microscopy-n', 'chemist-n', 'laboratory-n', 'jonathan-n', 'tourism-n', 'williams-n', 'investigator-n', 'expert-n', 'helen-n', 'james-n', 'people-n', 'geologist-n', 'subject-n', 'case-n', 'simon-n', 'cambridge-n', 'peter-n', 'graduate-n', 'newton-n', 'mathematician-n', 'college-n', 'diffraction-n', 'commission-n', 'linguist-n', 'nick-n', 'rachel-n', 'martin-n', 'sarah-n', 'physicist-n', 'spectrometry-n', 'leeds-n', 'catherine-n', 'unit-n', 'zoologist-n', 'michael-n', 'applicant-n', 'thomas-n', 'geographer-n', 'course-n', 'girl-n', 'committee-n', 'matt-n', 'canada-n', 'lee-n', 'oxford-n', 'klein-n', 'trainee-n', 'matthew-n', 'york-n', 'majority-n', 'bruce-n', 'physiologist-n', 'evans-n', 'christopher-n', 'ben-n', 'institute-n', 'cooper-n', 'philosopher-n', 'paul-n', 'boy-n']

        self.assertEqual('adult-n', realResult['queried']['word'])
	wordNotAppeared = True
	nodes = realResult['nodes']
	for w in wordList:
	    if w in nodes:
		wordNotAppeared = False
        self.assertEqual(True, wordNotAppeared)

    def test_processModelA1(self):
	realResult = process('invest-v','money-n', 'A1', True, 20)
	wordList = ['time-n', 'sum-n', 'fund-n', 'resource-n', 'amount-n', 'capital-n', 'million-n', 'lot-n', 'saving-n', 'cash-n', 'energy-n', 'billion-n', 'pound-n', 'effort-n', 'share-n', 'dollar-n', 'deal-n', 'asset-n', 'technology-n']
	
	self.assertEqual('money-n', realResult['queried']['word'])
	wordNotAppeared = True
	nodes = realResult ['nodes']
	for w in wordList:
	    if w in nodes:
	        wordNotApeared = False
	self.assertEqual(True, wordNotAppeared)
	

 

    def test_process_exception_MBR_VEC_EMPTY(self):
        result = {'errCode' : errorCode.MBR_VEC_EMPTY}
        self.assertEqual(result, process('asdf', 'apple-n', 'A0', True, 20))

    def test_process_exception_QUERY_EMPTY(self):
        result = {'errCode' : errorCode.QUERY_EMPTY}
        self.assertEqual(result, process('eat-v', 'asdf', 'A0', True, 20))

    def test_process_exception_SMT_ROLE_EMPTY(self):
        result = {'errCode' : errorCode.SMT_ROLE_EMPTY}
        self.assertEqual(result, process('eat-v', 'apple-n', 'AM-MOD', True, 20))

# TODO add other test
