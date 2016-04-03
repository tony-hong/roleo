'''
    This module contains the url patterns for view2D app.
    It should be included in the url.py in wsvt module.
'''
from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^help/', views.help, name='help'),
    url(r'^contact/', views.contact, name='contact'),
    url(r'^impressum/', views.impressum, name='impressum'),
    url(r'^query/', views.query, name='query'),
    # The url hook for change model function 
    url(r'^changeModel/', views.changeModel, name='changeModel'),
    url(r'^errorCodeJSON/', views.errorCodeJSON, name='errorCodeJSON'),
    

]
