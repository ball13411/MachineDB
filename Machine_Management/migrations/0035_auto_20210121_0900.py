# Generated by Django 3.0.8 on 2021-01-21 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0034_machine_machine_asset_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_code', models.CharField(max_length=30, unique=True)),
                ('department_name', models.CharField(default=None, max_length=40, null=True)),
            ],
            options={
                'db_table': 'Department',
                'ordering': ['department_code'],
            },
        ),
        migrations.AlterField(
            model_name='user',
            name='user_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='departments',
            field=models.ManyToManyField(to='Machine_Management.Department'),
        ),
    ]