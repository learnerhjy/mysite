# Generated by Django 2.1.3 on 2019-10-26 11:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('read_statistics', '0006_auto_20191020_2016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readdetail',
            name='read_date',
            field=models.DateField(default=datetime.date(2019, 10, 26)),
        ),
    ]
