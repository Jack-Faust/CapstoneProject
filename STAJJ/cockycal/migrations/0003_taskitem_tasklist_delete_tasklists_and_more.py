# Generated by Django 4.1.7 on 2023-03-30 21:34

import cockycal.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cockycal", "0002_tasklists_delete_taskitem_delete_tasklist"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskItem",
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
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "due_date",
                    models.DateTimeField(default=cockycal.models.one_week_hence),
                ),
                (
                    "checked",
                    models.BooleanField(default=False, verbose_name="Approved"),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["due_date"],},
        ),
        migrations.CreateModel(
            name="TaskList",
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
                ("title", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.DeleteModel(name="TaskLists",),
        migrations.AddField(
            model_name="taskitem",
            name="task_list",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="cockycal.tasklist"
            ),
        ),
    ]
