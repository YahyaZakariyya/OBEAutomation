# Generated by Django 5.0.4 on 2024-10-03 01:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obesystem', '0018_programlearningoutcome_weightage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programlearningoutcome',
            name='PLO',
            field=models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12'), (13, '13'), (14, '14'), (15, '15')], validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
