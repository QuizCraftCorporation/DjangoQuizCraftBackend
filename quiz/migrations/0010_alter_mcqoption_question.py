# Generated by Django 4.2.2 on 2023-06-18 23:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "quiz",
            "0009_alter_insertionquestion_id_alter_mcqquestion_id_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="mcqoption",
            name="question",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="options",
                to="quiz.mcqquestion",
                verbose_name="question",
            ),
        ),
    ]
