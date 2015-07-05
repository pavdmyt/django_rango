# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0004_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='first_visit',
            field=models.DateTimeField(null=True, verbose_name=b'first visit', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='last_visit',
            field=models.DateTimeField(null=True, verbose_name=b'last visit', blank=True),
            preserve_default=True,
        ),
    ]
