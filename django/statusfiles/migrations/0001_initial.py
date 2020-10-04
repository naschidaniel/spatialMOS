# Generated by Django 3.1 on 2020-10-04 17:59

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StatusChecks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taskname', models.CharField(max_length=500)),
                ('cmd_regex', models.CharField(max_length=500)),
                ('name', models.CharField(max_length=100)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('max_age', models.IntegerField(default=60)),
                ('verified_by_admin', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['max_age', 'taskname', 'cmd_regex'],
            },
        ),
        migrations.CreateModel(
            name='StatusFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_finished_time', models.DateTimeField()),
                ('cmd', models.CharField(max_length=500)),
                ('date_imported', models.DateTimeField(default=django.utils.timezone.now)),
                ('check_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuscheck', to='statusfiles.statuschecks')),
            ],
            options={
                'ordering': ['task_finished_time', 'check_name', 'cmd'],
            },
        ),
    ]
