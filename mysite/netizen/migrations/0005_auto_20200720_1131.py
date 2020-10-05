# Generated by Django 3.0.8 on 2020-07-20 06:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('netizen', '0004_auto_20200720_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='description',
            field=models.TextField(default=1, max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='template',
            name='thumbnail',
            field=models.ImageField(default='hi', upload_to='media/templates/thumbs'),
        ),
        migrations.AddField(
            model_name='template',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='templates', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
