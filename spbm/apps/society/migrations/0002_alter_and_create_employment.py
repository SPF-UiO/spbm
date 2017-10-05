import django
from django.db import migrations, models


def create_employment(apps, schema_editor):
    """ One-way employment creation from workers """
    Worker = apps.get_model("society", "Worker")
    Employment = apps.get_model("society", "Employment")
    db_alias = schema_editor.connection.alias
    for worker in Worker.objects.using(db_alias).all():
        Employment.objects.create(worker=worker, society=worker.society, active=worker.active)


class Migration(migrations.Migration):
    dependencies = [
        ('society', '0001_squashed_app_merges'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(help_text='The date of the event in the format of <em>YYYY-MM-DD</em>.', verbose_name='event date'),
        ),
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(help_text='Name or title describing the event.', max_length=100, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='event',
            name='registered',
            field=models.DateField(auto_now_add=True, help_text='Date of event registration.', verbose_name='registered'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='hours',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.25)], verbose_name='hours'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='wage',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(10)], verbose_name='wage'),
        ),
        migrations.CreateModel(
            name='Employment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('society', models.ForeignKey(on_delete=models.PROTECT, to='society.Society')),
            ],
        ),
        migrations.AddField(
            model_name='worker',
            name='societies',
            field=models.ManyToManyField(related_name='workers', through='society.Employment', to='society.Society'),
        ),
        migrations.AddField(
            model_name='employment',
            name='worker',
            field=models.ForeignKey(on_delete=models.CASCADE, to='society.Worker'),
        ),
        migrations.AlterUniqueTogether(
            name='employment',
            unique_together=set([('worker', 'society')]),
        ),
        migrations.RunPython(
            create_employment,
        ),
        migrations.RemoveField(
            model_name='worker',
            name='society',
        ),
    ]
