# Generated by Django 5.2.3 on 2025-07-03 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_classgroup_teachergroup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classgroup',
            name='class_names',
        ),
        migrations.AddField(
            model_name='classgroup',
            name='students',
            field=models.ManyToManyField(related_name='class_groups', to='accounts.student'),
        ),
    ]
