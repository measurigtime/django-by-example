# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0006_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='categories_liked',
            field=models.ManyToManyField(related_name=b'users_who_like', to='rango.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pages_liked',
            field=models.ManyToManyField(related_name=b'users_who_like', to='rango.Page'),
            preserve_default=True,
        ),
    ]
