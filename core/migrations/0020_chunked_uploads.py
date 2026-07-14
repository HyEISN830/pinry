import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_align_proxy_model_references'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadRateBucket',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('actor_key', models.CharField(max_length=128, unique=True)),
                ('available_at', models.DateTimeField()),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChunkedUpload',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'target',
                    models.CharField(
                        choices=[('image', 'image'), ('avatar', 'avatar')],
                        max_length=16,
                    ),
                ),
                ('filename', models.CharField(max_length=255)),
                ('content_type', models.CharField(blank=True, max_length=127)),
                ('total_size', models.PositiveIntegerField()),
                ('received_size', models.PositiveIntegerField(default=0)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('uploading', 'uploading'),
                            ('processing', 'processing'),
                            ('complete', 'complete'),
                            ('failed', 'failed'),
                        ],
                        db_index=True,
                        default='uploading',
                        max_length=16,
                    ),
                ),
                ('client_key', models.CharField(blank=True, db_index=True, max_length=96)),
                ('ip_hash', models.CharField(blank=True, db_index=True, max_length=96)),
                ('error', models.TextField(blank=True)),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('expires', models.DateTimeField(db_index=True)),
                (
                    'image',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='chunked_uploads',
                        to='core.Image',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='chunked_uploads',
                        to='users.User',
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name='chunkedupload',
            index=models.Index(
                fields=['user', 'status', 'updated'],
                name='core_chunk_user_status_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='chunkedupload',
            index=models.Index(
                fields=['ip_hash', 'status', 'updated'],
                name='core_chunk_ip_status_idx',
            ),
        ),
    ]
