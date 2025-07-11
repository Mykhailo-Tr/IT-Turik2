# Generated by Django 5.2.3 on 2025-07-02 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('class_names', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='TeacherGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('teachers', models.ManyToManyField(related_name='groups', to='accounts.teacher')),
            ],
        ),
    ]
