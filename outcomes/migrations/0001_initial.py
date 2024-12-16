# Generated by Django 5.0.4 on 2024-12-16 11:41

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramLearningOutcome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PLO', models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12'), (13, '13'), (14, '14'), (15, '15')], validators=[django.core.validators.MinValueValidator(1)])),
                ('heading', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('weightage', models.FloatField(help_text='PLO weightage must be between 0.0 and 100.0', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
            ],
        ),
        migrations.CreateModel(
            name='CourseLearningOutcome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CLO', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12'), (13, '13'), (14, '14'), (15, '15')], validators=[django.core.validators.MinValueValidator(1)])),
                ('heading', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('weightage', models.FloatField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_outcomes', to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='PloCloMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weightage', models.FloatField()),
                ('clo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_mappings', to='outcomes.courselearningoutcome')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_clo_mappings', to='courses.course')),
            ],
        ),
    ]
