from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_image_fetch_jobs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comiclike',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='users.User',
            ),
        ),
        migrations.AlterField(
            model_name='comicpage',
            name='image',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='comic_pages',
                to='core.Image',
            ),
        ),
        migrations.AlterField(
            model_name='imagefetchjob',
            name='image',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='fetch_jobs',
                to='core.Image',
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
                to='core.Image',
            ),
        ),
        migrations.AlterField(
            model_name='pinlike',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='users.User',
            ),
        ),
    ]
