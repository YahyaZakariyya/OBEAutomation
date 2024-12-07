# Generated by Django 5.0.4 on 2024-11-20 08:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obesystem', '0028_courselearningoutcome_weightage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assessment',
            name='marks',
        ),
        migrations.AddField(
            model_name='assessment',
            name='weightage',
            field=models.FloatField(default=1, help_text="Percentage contribution within the type's weightage (e.g., 25% of the total 15% for Assignments).", validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='type',
            field=models.CharField(choices=[('quiz', 'Quiz'), ('assignment', 'Assignment'), ('midterm', 'Midterm'), ('final', 'Final Exam'), ('lab', 'Lab'), ('project', 'Project')], max_length=20),
        ),
    ]
