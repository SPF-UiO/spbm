# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('society', '0005_events_create_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='invoice',
            field=models.ForeignKey(blank=True, to='invoices.Invoice', verbose_name='invoice', related_name='events',
                                    null=True),
        ),
        migrations.AlterField(
            model_name='shift',
            name='event',
            field=models.ForeignKey(to='society.Event', related_name='shifts'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='norlonn_report',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='norlonn.NorlonnReport', verbose_name='norl&oslash;nn report',
                                    related_name='shifts', null=True),
        ),
        migrations.AlterField(
            model_name='shift',
            name='worker',
            field=models.ForeignKey(to='society.Worker', on_delete=django.db.models.deletion.PROTECT,
                                    related_name='shifts', verbose_name='worker'),
        ),
    ]
