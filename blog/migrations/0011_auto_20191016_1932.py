# Generated by Django 2.1.3 on 2019-10-16 11:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_auto_20191016_1129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='readnum',
            name='blog',
        ),
        migrations.DeleteModel(
            name='ReadNum',
        ),
    ]
