# Generated by Django 4.2.2 on 2023-06-30 10:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quiz", "0015_remove_mcqquestion_answer_remove_quiz_source_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="quiz",
            name="private",
            field=models.BooleanField(default=False),
        ),
    ]