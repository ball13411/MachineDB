# Generated by Django 3.0.8 on 2021-01-21 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0033_auto_20210120_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='machine_asset_code',
            field=models.CharField(default=None, max_length=30, null=True),
        ),
    ]