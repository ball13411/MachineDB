# Generated by Django 3.0.8 on 2020-08-06 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0023_auto_20200806_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screen',
            name='screen_id',
            field=models.CharField(max_length=15, primary_key=True, serialize=False),
        ),
    ]
