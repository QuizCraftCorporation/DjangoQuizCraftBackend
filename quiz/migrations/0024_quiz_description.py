# Generated by Django 4.2.2 on 2023-07-08 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0023_remove_quiz_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]