# Generated by Django 4.2.2 on 2023-06-18 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("quiz", "0006_remove_mcqquestion_options_mcqoption_question"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="quiz",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="quiz.quiz"
            ),
            preserve_default=False,
        ),
    ]
