from django.db import models

class SemanticRole(models.Model):
    name = models.CharField(max_length=10)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.name