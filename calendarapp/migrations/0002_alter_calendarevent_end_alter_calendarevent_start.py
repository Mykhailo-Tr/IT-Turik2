# Generated by Django 5.2.4 on 2025-07-06 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendarapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendarevent',
            name='end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='calendarevent',
            name='start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
