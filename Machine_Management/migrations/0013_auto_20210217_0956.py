# Generated by Django 3.0.8 on 2021-02-17 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0012_auto_20210210_1243'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='menu',
            options={'ordering': ['level', 'index']},
        ),
        migrations.AddField(
            model_name='maintenance_job',
            name='is_report',
            field=models.BooleanField(default=False),
        ),
    ]
