# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('society', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=1000)),
                ('address', models.CharField(max_length=1000)),
                ('account_no', models.CharField(blank=True, max_length=20)),
                ('person_id', models.CharField(blank=True, max_length=20)),
                ('norlonn_number', models.IntegerField(unique=True, blank=True, null=True)),
                ('society', models.ForeignKey(to='society.Society', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
