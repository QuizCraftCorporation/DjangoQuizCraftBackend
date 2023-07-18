# Generated by Django 4.2.2 on 2023-07-08 22:22

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quiz", "0025_quizview"),
    ]

    operations = [
        migrations.AlterField(
            model_name="quizview",
            name="datetime",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="datetime"
            ),
        ),
    ]
