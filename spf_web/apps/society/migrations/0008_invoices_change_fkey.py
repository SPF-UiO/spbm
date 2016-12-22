# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('society', '0007_invoices_create'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='invoice',
            field=models.ForeignKey(to='society.Invoice', blank=True, related_name='events', null=True,
                                    verbose_name='invoice'),
        ),
    ]
