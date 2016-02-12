'''
    This module contains the models of view2D app.
    All models are associated to a schema in database.

    @Author: 
        Tony Hong
'''
from django.db import models

class SemanticRole(models.Model):
    name = models.CharField(max_length=10)
    description = models.CharField(default = '', max_length=64)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.name

# TODO: hook for 'change semantic model'
# class SemanticModel(models.Model):
#     name = models.CharField(max_length=10)
#     description = models.CharField(default = '', max_length=256)
#     def __unicode__(self):              # __unicode__ on Python 2
#         return self.name