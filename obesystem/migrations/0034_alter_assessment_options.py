# Generated by Django 5.0.4 on 2024-11-29 19:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('obesystem', '0033_alter_section_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assessment',
            options={'permissions': [('can_add_question', 'Can add question to this assessment')]},
        ),
    ]