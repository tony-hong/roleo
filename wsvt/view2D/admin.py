'''
    This module is used to configure the SemanticRole in models in admin page, 
    so that the admin can configure the value of SemanticRole in admin page

    @Author: 
        Tony Hong
'''
from django.contrib import admin

from .models import SemanticRole

admin.site.register(SemanticRole)
