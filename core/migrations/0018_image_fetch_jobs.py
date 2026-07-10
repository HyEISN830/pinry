from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_likes_audit_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comicpage',
            name='image',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='comic_pages',
                to='django_images.image',
            ),
        ),
        migrations.AlterField(
            model_name='pin',
            name='image',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='pin',
                to='django_images.image',
            ),
        ),
        migrations.CreateModel(
            name='ImageFetchJob',
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
                ('source_url', models.CharField(max_length=2048)),
                (
                    'referer',
                    models.CharField(blank=True, max_length=2048, null=True),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'pending'),
                            ('processing', 'processing'),
                            ('ready', 'ready'),
                            ('failed', 'failed'),
                        ],
                        db_index=True,
                        default='pending',
                        max_length=16,
                    ),
                ),
                ('error', models.TextField(blank=True)),
                ('attempts', models.PositiveIntegerField(default=0)),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('started', models.DateTimeField(blank=True, null=True)),
                ('finished', models.DateTimeField(blank=True, null=True)),
                (
                    'comic_page',
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='image_fetch_job',
                        to='core.comicpage',
                    ),
                ),
                (
                    'image',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='fetch_jobs',
                        to='django_images.image',
                    ),
                ),
                (
                    'pin',
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='image_fetch_job',
                        to='core.pin',
                    ),
                ),
            ],
            options={
                'indexes': [
                    models.Index(
                        fields=['status', 'published'],
                        name='core_imgfetch_status_idx',
                    ),
                    models.Index(
                        fields=['status', 'started'],
                        name='core_imgfetch_stale_idx',
                    ),
                ],
            },
        ),
    ]
