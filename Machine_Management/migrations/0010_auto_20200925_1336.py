# Generated by Django 3.0.8 on 2020-09-25 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0009_auto_20200924_1508'),
    ]

    operations = [
        migrations.RenameField(
            model_name='machine',
            old_name='machine_capacity_per_minute',
            new_name='machine_load_capacity',
        ),
        migrations.RenameField(
            model_name='machine',
            old_name='machine_capacity_measure_unit',
            new_name='machine_load_capacity_unit',
        ),
        migrations.AddField(
            model_name='machine',
            name='machine_emp_contact',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='machine',
            name='machine_brand',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='machine',
            name='machine_emp_id_response',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='machine',
            name='machine_model',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='machine',
            name='machine_supplier_code',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
