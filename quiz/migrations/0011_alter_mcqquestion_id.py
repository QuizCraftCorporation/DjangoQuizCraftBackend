# Generated by Django 4.2.2 on 2023-06-18 23:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("quiz", "0010_alter_mcqoption_question"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mcqquestion",
            name="id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="quiz.question",
                verbose_name="question id",
            ),
        ),
    ]