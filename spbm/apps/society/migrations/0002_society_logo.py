# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('society', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='society',
            name='logo',
            field=models.FileField(upload_to='', null=True),
            preserve_default=True,
        ),
    ]
