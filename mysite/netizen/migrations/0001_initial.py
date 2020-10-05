# Generated by Django 3.0.8 on 2020-07-20 04:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('images', models.ImageField(upload_to='media/templates')),
                ('thumbnail', models.ImageField(default='hi', upload_to='media/templates/thumbs')),
                ('description', models.TextField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Meme',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('images', models.ImageField(upload_to='media/memes/')),
                ('description', models.TextField(max_length=250)),
                ('thumbnail', models.ImageField(default='hi', upload_to='media/memes/thumbs')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('template', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='template_memes', to='netizen.Template')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
