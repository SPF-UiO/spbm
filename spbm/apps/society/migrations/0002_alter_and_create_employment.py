import django
from django.db import migrations, models
from django.db.models import Count


def create_employment(apps, schema_editor):
    """ One-way employment creation from workers """

    Worker = apps.get_model("society", "Worker")
    Shift = apps.get_model("society", "Shift")
    Employment = apps.get_model("society", "Employment")
    db_alias = schema_editor.connection.alias

    # First, let's find the duplicate workers that exist in their correct order
    duplicated_person_ids = (
        Worker.objects.using(db_alias).values('person_id')
            .annotate(count=Count('id'))
            .values('person_id')
            .order_by()
            .filter(count__gt=1)
            .exclude(person_id='')
    )
    duplicated_workers = Worker.objects.using(db_alias) \
        .filter(person_id__in=duplicated_person_ids) \
        .exclude(person_id='') \
        .order_by('id')

    # Followed by reassigning all the shifts and whatnots -- we can do this without having Employments ready!
    for dup_id in duplicated_person_ids:
        # we get the workers in this way to make sure we don't go over the canonical worker again, creating duplicated
        # unneccessary Employments
        worker = Worker.objects.using(db_alias).filter(person_id=dup_id['person_id']).order_by('id').first()

        print("Processing: {name} ({id}): {sn}".format(name=worker.name, id=worker.id, sn=worker.society.shortname))
        Employment.objects.using(db_alias).create(worker=worker, society=worker.society, active=worker.active)
        Shift.objects.using(db_alias)\
            .filter(worker__person_id=worker.person_id)\
            .exclude(worker__pk=worker.pk)\
            .update(worker=worker)

        # Create Employments for non-same society duplicates (UNIQUE constraint)
        for dups in duplicated_workers.filter(person_id=worker.person_id) \
                .exclude(id=worker.id).exclude(society=worker.society):
            print(" - Employment: {name} ({sn}): {id}".format(name=dups.name, id=dups.id, sn=dups.society.shortname))
            Employment.objects.using(db_alias).create(worker=worker, society=dups.society, active=dups.active)

        # Change activeness and name for all duplicates, no matter the society
        # Note that we also blank their national ID, so that we can migrate safely to that come next migration.
        for dups in duplicated_workers.filter(person_id=worker.person_id).exclude(id=worker.id):
            print(" - Deactivation: {name} ({sn}): {id}".format(name=dups.name, sn=dups.society.shortname, id=dups.id))
            dups.active = False
            dups.name = "DUPLICATE: " + dups.name
            dups.person_id = None
            dups.save()

    # Ensure that we clean up all blank objects
    print("Nulling out blank workers IDs:")
    for blank_worker_person_id in Worker.objects.using(db_alias).filter(person_id=""):
        blank_worker_person_id.person_id = None
        blank_worker_person_id.save()
        print(" - {} ({} job(s))".format(blank_worker_person_id.name, blank_worker_person_id.shifts.count()))

    # Last, but not least, create Employment relationships for all non-duplicates
    for worker in Worker.objects.using(db_alias).filter(employment__isnull=True):
        Employment.objects.using(db_alias).create(worker=worker, society=worker.society, active=worker.active)


class Migration(migrations.Migration):
    dependencies = [
        ('society', '0001_squashed_app_merges'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(help_text='The date of the event in the format of <em>YYYY-MM-DD</em>.',
                                   verbose_name='event date'),
        ),
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(help_text='Name or title describing the event.', max_length=100,
                                   verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='event',
            name='registered',
            field=models.DateField(auto_now_add=True, help_text='Date of event registration.',
                                   verbose_name='registered'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='hours',
            field=models.DecimalField(decimal_places=2, max_digits=10,
                                      validators=[django.core.validators.MinValueValidator(0.25)],
                                      verbose_name='hours'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='wage',
            field=models.DecimalField(decimal_places=2, max_digits=10,
                                      validators=[django.core.validators.MinValueValidator(10)], verbose_name='wage'),
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
            unique_together={('worker', 'society')},
        ),
        # Allow for nulling out
        migrations.AlterField(
            model_name='worker',
            name='person_id',
            field=models.CharField(blank=True, null=True, unique=False, max_length=20, verbose_name='person id'),
        ),
        # The most important part: one-way migration.
        migrations.RunPython(
            create_employment,
        ),
        # Get rid of the old society field
        migrations.RemoveField(
            model_name='worker',
            name='society',
        ),
        # Let's make it unique
        migrations.AlterField(
            model_name='worker',
            name='person_id',
            field=models.CharField(blank=True, null=True, unique=True, max_length=20, verbose_name='person ID'),
        ),
    ]
