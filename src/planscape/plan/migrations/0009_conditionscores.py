# Generated by Django 4.1.3 on 2023-01-25 20:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("conditions", "0003_get_mean_condition_score"),
        ("plan", "0008_projectarea_owner"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConditionScores",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mean_score", models.FloatField(null=True)),
                (
                    "condition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="conditions.condition",
                    ),
                ),
                (
                    "plan",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="plan.plan",
                    ),
                ),
                (
                    "project_area",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="plan.projectarea",
                    ),
                ),
            ],
        ),
    ]