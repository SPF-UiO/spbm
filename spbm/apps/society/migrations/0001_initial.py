# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Society',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('shortname', models.CharField(max_length=10)),
                ('invoice_email', models.EmailField(default='', max_length=75)),
                ('default_wage', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
