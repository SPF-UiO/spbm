# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('society', '0003_auto_20160715_1423'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(help_text='Check off if the worker is still actively working.',
                                               verbose_name='active', default=True)),
                ('name',
                 models.CharField(verbose_name='name', max_length=1000, help_text='Full name, with first name first.')),
                ('address', models.CharField(verbose_name='address', max_length=1000,
                                             help_text='Full address including postal code and area.')),
                ('account_no', models.CharField(verbose_name='account no.', blank=True,
                                                help_text='Norwegian bank account number, no periods, 11 digits.',
                                                max_length=20)),
                ('person_id', models.CharField(blank=True, max_length=20)),
                ('norlonn_number', models.IntegerField(
                    help_text='Employee number in the wage system, Norl&oslash;nn. <strong>Must</strong> exist and be correct!',
                    verbose_name='norl&oslash;nn number', blank=True, unique=True, null=True)),
                ('society', models.ForeignKey(to='society.Society', on_delete=django.db.models.deletion.PROTECT,
                                              related_name='workers')),
            ],
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
