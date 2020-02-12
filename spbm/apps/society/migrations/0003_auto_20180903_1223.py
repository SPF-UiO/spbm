# Generated by Django 2.0.6 on 2018-09-03 12:23

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('society', '0002_alter_and_create_employment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='society',
            name='default_wage',
            field=models.DecimalField(decimal_places=2, default=Decimal('160'), max_digits=10, verbose_name='default wage per hour'),
        ),
    ]