# Generated by Django 3.0.8 on 2020-08-15 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20200722_1453'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='bio',
            new_name='about',
        ),
    ]
