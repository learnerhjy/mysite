# Generated by Django 2.1.3 on 2019-10-19 09:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('read_statistics', '0004_auto_20191018_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readdetail',
            name='read_date',
            field=models.DateField(default=datetime.date(2019, 10, 19)),
        ),
    ]
