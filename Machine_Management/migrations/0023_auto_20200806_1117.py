# Generated by Django 3.0.8 on 2020-08-06 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0022_auto_20200805_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screen',
            name='file_py',
            field=models.CharField(max_length=20),
        ),
    ]