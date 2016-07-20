# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('society', '0002_society_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='society',
            name='invoice_email',
            field=models.EmailField(max_length=254, default=''),
        ),
    ]
