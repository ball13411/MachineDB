# Generated by Django 3.0.8 on 2020-09-15 08:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0016_auto_20200915_0751'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine_type',
            name='line',
        ),
    ]
