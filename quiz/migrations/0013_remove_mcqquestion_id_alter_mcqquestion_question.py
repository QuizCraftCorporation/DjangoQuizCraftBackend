# Generated by Django 4.2.2 on 2023-06-18 23:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("quiz", "0012_mcqquestion_question_alter_mcqquestion_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mcqquestion",
            name="id",
        ),
        migrations.AlterField(
            model_name="mcqquestion",
            name="question",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="quiz.question",
                verbose_name="question id",
            ),
        ),
    ]