# Generated by Django 3.0.8 on 2020-09-18 14:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0004_auto_20200918_1432'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maintenance_plan',
            name='job',
        ),
    ]