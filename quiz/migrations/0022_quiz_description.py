# Generated by Django 4.2.2 on 2023-07-08 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quiz", "0021_alter_insertionquestion_question_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="quiz",
            name="description",
            field=models.TextField(default="", max_length=400),
            preserve_default=False,
        ),
    ]
