# Generated by Django 4.2.2 on 2023-07-02 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("quiz", "0020_alter_insertionquestion_question_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="insertionquestion",
            name="question",
            field=models.OneToOneField(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="insertion_question",
                serialize=False,
                to="quiz.question",
                verbose_name="question id",
            ),
        ),
        migrations.AlterField(
            model_name="mcqquestion",
            name="question",
            field=models.OneToOneField(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="mcq_question",
                serialize=False,
                to="quiz.question",
                verbose_name="question id",
            ),
        ),
        migrations.AlterField(
            model_name="openendedquestion",
            name="question",
            field=models.OneToOneField(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="open_ended_question",
                serialize=False,
                to="quiz.question",
                verbose_name="question id",
            ),
        ),
        migrations.AlterField(
            model_name="truefalsequestion",
            name="question",
            field=models.OneToOneField(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="true_false_question",
                serialize=False,
                to="quiz.question",
                verbose_name="question id",
            ),
        ),
    ]
