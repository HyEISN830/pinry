# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, max_length=255, upload_to=users.models.avatar_upload_path)),
                ('avatar_small', models.ImageField(blank=True, max_length=255, upload_to=users.models.avatar_upload_path)),
                ('avatar_medium', models.ImageField(blank=True, max_length=255, upload_to=users.models.avatar_upload_path)),
                ('avatar_large', models.ImageField(blank=True, max_length=255, upload_to=users.models.avatar_upload_path)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pinry_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
