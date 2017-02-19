# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('society', '0004_worker'),
        ('events', '0004_auto_20150602_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(verbose_name='event date'),
        ),
        migrations.AlterField(
            model_name='event',
            name='invoice',
            field=models.ForeignKey(null=True, verbose_name='invoice', to='invoices.Invoice', blank=True,
                                    on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(verbose_name='name', max_length=100),
        ),
        migrations.AlterField(
            model_name='event',
            name='processed',
            field=models.DateField(null=True, verbose_name='processed', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='registered',
            field=models.DateField(auto_now_add=True, verbose_name='registered'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='hours',
            field=models.DecimalField(verbose_name='hours', max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='shift',
            name='norlonn_report',
            field=models.ForeignKey(null=True, verbose_name='norl&oslash;nn report',
                                    on_delete=django.db.models.deletion.SET_NULL, to='norlonn.NorlonnReport',
                                    blank=True),
        ),
        migrations.AlterField(
            model_name='shift',
            name='wage',
            field=models.DecimalField(verbose_name='wage', max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='shift',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='worker',
                                    to='society.Worker'),
        ),
    ]
