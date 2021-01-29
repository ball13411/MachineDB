# Generated by Django 3.0.8 on 2021-01-29 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0005_auto_20210127_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='repair_notice',
            name='is_receive',
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='repair_notice',
            name='receive_remark',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='repair_notice',
            name='receive_user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Machine_Management.User'),
        ),
    ]