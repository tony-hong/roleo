'''
    This module contains the models of view2D app.
    All models are associated to a schema in database.

    @Author: 
        Tony Hong
'''
from django.db import models

class SemanticRole(models.Model):
    labelSDDM = models.CharField(default = 'null', max_length=32)
    labelTypeDM = models.CharField(default = 'null', max_length=32)
    name = models.CharField(default = 'null', max_length=32)
    
    # 1: SDDM only; 
    # 2: both SDDM and RBE 
    # 3: both SDDM, RBE and TypeDM; 
    modelSupport = models.IntegerField(default = 1)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.name