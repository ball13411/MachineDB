# Generated by Django 3.0.8 on 2020-09-18 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0003_machine_and_spare_part_last_maintenance_hour'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='machine_hour',
            field=models.IntegerField(default=1200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='maintenance_plan',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Machine_Management.Maintenance_order_head'),
        ),
    ]
