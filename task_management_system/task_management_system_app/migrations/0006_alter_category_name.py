# Generated by Django 5.1.3 on 2024-11-22 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_management_system_app', '0005_alter_task_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
