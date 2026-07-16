from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_images', '0002_auto_20180826_0814'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='image',
            index=models.Index(
                fields=['image'],
                name='django_images_image_path_idx',
            ),
        ),
    ]
