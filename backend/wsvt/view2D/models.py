from django.db import models

class SemanticRole(models.Model):
    name = models.CharField(max_length=10)
    description = models.CharField(default = '', max_length=64)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.name

# class SemanticModel(models.Model):
#     name = models.CharField(max_length=10)
#     description = models.CharField(default = '', max_length=256)
#     def __unicode__(self):              # __unicode__ on Python 2
#         return self.name