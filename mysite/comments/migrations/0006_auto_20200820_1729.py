# Generated by Django 3.0.8 on 2020-08-20 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0005_auto_20200820_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
