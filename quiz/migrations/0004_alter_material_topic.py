# Generated by Django 4.2.2 on 2023-06-18 20:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("quiz", "0003_rename_file_name_material_file_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="material",
            name="topic",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="quiz.topic",
                verbose_name="topic",
            ),
        ),
    ]
