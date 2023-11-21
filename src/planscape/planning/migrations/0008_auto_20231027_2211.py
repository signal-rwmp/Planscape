# Generated by Django 4.1.11 on 2023-10-27 22:11

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("planning", "0007_auto_20231027_2211"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scenario",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
