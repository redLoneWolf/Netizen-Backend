# Generated by Django 3.0.8 on 2020-08-31 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netizen', '0010_auto_20200831_1228'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imagemodel',
            old_name='images',
            new_name='image',
        ),
    ]
