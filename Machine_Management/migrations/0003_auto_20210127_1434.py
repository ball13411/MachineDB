# Generated by Django 3.0.8 on 2021-01-27 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0002_auto_20210126_0821'),
    ]

    operations = [
        migrations.AddField(
            model_name='repair_notice',
            name='approve_remark',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='repair_notice',
            name='inspect_remark',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='repair_notice',
            name='is_cancel',
            field=models.BooleanField(default=False),
        ),
    ]
