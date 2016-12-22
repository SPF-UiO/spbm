# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0001_initial'),
        ('society', '0008_invoices_change_fkey'),
    ]

    database_operations = [
        migrations.AlterModelTable('Invoice', 'society_invoice')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(database_operations=database_operations)
    ]
