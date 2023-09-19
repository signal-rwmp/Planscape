# Generated by Django 4.1.3 on 2023-02-14 04:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("conditions", "0004_get_condition_pixels"),
        ("plan", "0009_remove_project_max_cost_project_max_budget_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="max_cost",
        ),
        migrations.AddField(
            model_name="project",
            name="max_budget",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="project",
            name="max_road_distance",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="project",
            name="max_slope",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="project",
            name="max_treatment_area_ratio",
            field=models.FloatField(null=True),
        ),
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
                ("sum", models.FloatField(null=True)),
                ("count", models.IntegerField(null=True)),
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
