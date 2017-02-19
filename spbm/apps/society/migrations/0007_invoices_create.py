# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('society', '0006_auto_20161222_1508'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('invoice_number', models.IntegerField(unique=True)),
                ('period', models.DateField()),
                ('paid', models.BooleanField(default=False)),
                ('society', models.ForeignKey(to='society.Society', related_name='invoices', on_delete=models.CASCADE)),
            ],
            options={
                'permissions': (
                    ('close_period', 'Can close periods to generate invoices'),
                    ('mark_paid', 'Can mark invoices as paid')),
            },
        ),
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together=set([('period', 'society')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
