# Generated by Django 5.0.4 on 2024-06-12 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obesystem', '0003_report_remove_assessment_total_marks_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='courselearningoutcome',
            name='name',
            field=models.CharField(default='Unnamed CLO', max_length=100),
        ),
        migrations.AddField(
            model_name='programlearningoutcome',
            name='name',
            field=models.CharField(default='Unnamed PLO', max_length=100),
        ),
    ]
