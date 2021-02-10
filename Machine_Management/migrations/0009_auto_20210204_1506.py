# Generated by Django 3.0.8 on 2021-02-04 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Machine_Management', '0008_auto_20210201_1440'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user_and_department',
            options={'ordering': ['department__department_code', 'user__firstname']},
        ),
        migrations.AddField(
            model_name='repair_notice',
            name='department_receive',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Machine_Management.Department'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='repair_notice',
            name='department_notifying',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Machine_Management.Department'),
        ),
    ]