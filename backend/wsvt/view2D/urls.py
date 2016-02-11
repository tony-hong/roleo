from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^help/', views.help, name='help'),
    url(r'^contact/', views.contact, name='contact'),
    url(r'^impressum/', views.impressum, name='impressum'),
    url(r'^query/', views.query, name='query'),
    url(r'^changeModel/', views.changeModel, name='changeModel'),
    url(r'^errorCodeJSON/', views.errorCodeJSON, name='errorCodeJSON'),
]
