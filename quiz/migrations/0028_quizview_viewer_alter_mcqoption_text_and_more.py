# Generated by Django 4.2.2 on 2023-07-14 07:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("quiz", "0027_remove_quizview_datetime_quiz_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="quizview",
            name="viewer",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="viewed_quizzes",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="mcqoption",
            name="text",
            field=models.CharField(max_length=200, verbose_name="option text"),
        ),
        migrations.AlterField(
            model_name="quizview",
            name="id",
            field=models.BigAutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
    ]
