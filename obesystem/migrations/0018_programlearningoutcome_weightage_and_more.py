# Generated by Django 5.0.4 on 2024-10-02 19:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obesystem', '0017_courselearningoutcome_weightage'),
    ]

    operations = [
        migrations.AddField(
            model_name='programlearningoutcome',
            name='weightage',
            field=models.FloatField(default=10, help_text='PLO weightage must be between 0 and 100.', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='programlearningoutcome',
            constraint=models.UniqueConstraint(fields=('program', 'PLO'), name='unique_plo_per_program'),
        ),
    ]
