# Generated by Django 3.0.8 on 2020-07-21 09:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netizen', '0005_auto_20200720_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meme',
            name='template',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='memes', to='netizen.Template'),
        ),
    ]
