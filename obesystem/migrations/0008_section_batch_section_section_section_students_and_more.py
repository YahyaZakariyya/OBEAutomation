# Generated by Django 5.0.4 on 2024-08-31 06:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obesystem', '0007_remove_enrollment_section_remove_enrollment_student_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='batch',
            field=models.CharField(choices=[('Spring', 'Spring'), ('Summer', 'Summer'), ('Fall', 'Fall')], default=2024, max_length=6),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='section',
            name='section',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J'), ('K', 'K'), ('L', 'L'), ('M', 'M'), ('N', 'N'), ('O', 'O'), ('P', 'P'), ('Q', 'Q'), ('R', 'R'), ('S', 'S'), ('T', 'T'), ('U', 'U'), ('V', 'V'), ('W', 'W'), ('X', 'X'), ('Y', 'Y'), ('Z', 'Z')], default='A', max_length=1),
        ),
        migrations.AddField(
            model_name='section',
            name='students',
            field=models.ManyToManyField(blank=True, limit_choices_to={'role': 'student'}, related_name='enrolled_sections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='section',
            name='year',
            field=models.CharField(choices=[('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'), ('2030', '2030'), ('2031', '2031'), ('2032', '2032'), ('2033', '2033')], default=2024, max_length=4),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='section',
            name='faculty',
            field=models.ForeignKey(limit_choices_to={'role': 'faculty'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='taught_sections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='section',
            name='semester',
            field=models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], default='1', max_length=2),
        ),
    ]
