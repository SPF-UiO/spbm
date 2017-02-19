# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('norlonn', '0002_auto_20150602_1738'),
        ('invoices', '0001_initial'),
        ('society', '0004_worker'),
        ('events', '0005_auto_20161218_1500'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('date', models.DateField(verbose_name='event date')),
                ('registered', models.DateField(auto_now_add=True, verbose_name='registered')),
                ('processed', models.DateField(null=True, blank=True, verbose_name='processed')),
                ('invoice', models.ForeignKey(null=True, verbose_name='invoice', related_name='in_invoice', blank=True,
                                              to='invoices.Invoice', on_delete=models.PROTECT)),
                ('society', models.ForeignKey(on_delete=models.PROTECT, related_name='society',
                                              to='society.Society')),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('wage', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='wage')),
                ('hours', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='hours')),
                ('event', models.ForeignKey(to='society.Event', on_delete=models.CASCADE)),
                ('norlonn_report',
                 models.ForeignKey(to='norlonn.NorlonnReport', null=True, verbose_name='norl&oslash;nn report',
                                   related_name='in_report', blank=True, on_delete=models.SET_NULL)),
                ('worker', models.ForeignKey(on_delete=models.PROTECT, verbose_name='worker',
                                             related_name='worker', to='society.Worker')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='shift',
            unique_together=set([('event', 'worker')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
