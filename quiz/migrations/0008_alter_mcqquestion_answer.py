# Generated by Django 4.2.2 on 2023-06-18 21:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quiz", "0007_question_quiz"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mcqquestion",
            name="answer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="quiz.mcqoption",
                verbose_name="answer id",
            ),
        ),
    ]
