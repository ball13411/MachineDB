# Generated by Django 3.0.8 on 2020-08-25 10:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0002_auto_20200825_0957'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine',
            name='machine_type',
        ),
    ]