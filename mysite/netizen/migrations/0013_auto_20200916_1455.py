# Generated by Django 3.0.8 on 2020-09-16 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netizen', '0012_auto_20200912_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meme',
            name='description',
            field=models.TextField(blank=True, max_length=250),
        ),
    ]
