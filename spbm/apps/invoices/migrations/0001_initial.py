# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('society', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('invoice_number', models.IntegerField(unique=True)),
                ('period', models.DateField()),
                ('paid', models.BooleanField(default=False)),
                ('society', models.ForeignKey(to='society.Society', on_delete=models.PROTECT)),
            ],
            options={
                'permissions': (('close_period', 'Can close periods to generate invoices'), ('mark_paid', 'Can mark invoices as paid')),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together=set([('period', 'society')]),
        ),
    ]
