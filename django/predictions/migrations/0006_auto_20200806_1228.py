# Generated by Django 3.0.9 on 2020-08-06 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('predictions', '0005_auto_20200806_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spatialmosstep',
            name='spatialmos_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='predictions.SpatialMosRun'),
        ),
    ]
