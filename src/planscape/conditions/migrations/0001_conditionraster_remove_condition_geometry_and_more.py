# Generated by Django 4.1.1 on 2022-11-14 16:04

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conditions', 'get_rast_tile'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConditionRaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raster_name', models.TextField(null=True)),
                ('raster', django.contrib.gis.db.models.fields.RasterField(null=True, srid=4326)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.RemoveField(
            model_name='condition',
            name='geometry',
        ),
        migrations.AddField(
            model_name='condition',
            name='raster_name',
            field=models.TextField(null=True),
        ),
    ]