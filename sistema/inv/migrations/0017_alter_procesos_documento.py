# Generated by Django 5.1.6 on 2025-03-18 21:20

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv', '0016_procesos_documento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='procesos',
            name='documento',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='C:/Temp'), upload_to='temp/'),
        ),
    ]
