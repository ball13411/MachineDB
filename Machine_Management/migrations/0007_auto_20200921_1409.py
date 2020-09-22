# Generated by Django 3.0.8 on 2020-09-21 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0006_auto_20200921_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='machine_minute',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='machine',
            name='machine_hour',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='machine_and_spare_part',
            name='last_maintenance_hour',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterModelTable(
            name='maintenance_order_detail',
            table='Maintenance_order_detail',
        ),
        migrations.AlterModelTable(
            name='maintenance_order_head',
            table='Maintenance_order_head',
        ),
        migrations.AlterModelTable(
            name='maintenance_plan',
            table='Maintenance_plan',
        ),
    ]
