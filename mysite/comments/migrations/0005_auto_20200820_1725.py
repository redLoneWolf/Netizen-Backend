# Generated by Django 3.0.8 on 2020-08-20 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0004_auto_20200730_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='updated',
            field=models.DateTimeField(),
        ),
    ]
