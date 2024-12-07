# Generated by Django 5.0.4 on 2024-11-29 17:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obesystem', '0031_alter_question_clo_alter_question_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='number',
        ),
        migrations.AlterField(
            model_name='assessment',
            name='weightage',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
    ]
