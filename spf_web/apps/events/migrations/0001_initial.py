# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0001_initial'),
        ('invoices', '0001_initial'),
        ('society', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('registered', models.DateField(auto_now_add=True)),
                ('processed', models.DateField(blank=True, null=True)),
                ('invoice', models.ForeignKey(to='invoices.Invoice', null=True, blank=True)),
                ('society', models.ForeignKey(to='society.Society', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('wage', models.DecimalField(decimal_places=2, max_digits=10)),
                ('hours', models.DecimalField(decimal_places=2, max_digits=10)),
                ('event', models.ForeignKey(to='events.Event')),
                ('worker', models.ForeignKey(to='workers.Worker')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='shift',
            unique_together=set([('event', 'worker')]),
        ),
    ]
