# Generated by Django 3.0.8 on 2020-09-18 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0002_maintenance_order_detail_maintenance_order_head_maintenance_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine_and_spare_part',
            name='last_maintenance_hour',
            field=models.IntegerField(default=1000),
            preserve_default=False,
        ),
    ]