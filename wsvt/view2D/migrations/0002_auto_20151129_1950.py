# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('view2D', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='semanticrole',
            old_name='role',
            new_name='name',
        ),
    ]
