import hashlib
import os


def upload_path(instance, filename, **kwargs):
    hasher = hashlib.md5()
    for chunk in instance.image.chunks():
        hasher.update(chunk)
    hash = hasher.hexdigest()
    base, ext = os.path.splitext(filename)
    return '%(first)s/%(second)s/%(hash)s/%(base)s%(ext)s' % {
        'first': hash[0],
        'second': hash[1],
        'hash': hash,
        'base': base,
        'ext': ext,
    }


def motion_photo_upload_path(instance, filename, **kwargs):
    hash = getattr(instance, '_video_hash', None)
    if not hash:
        image = getattr(instance, 'image', None)
        image_file = getattr(image, 'image', None)
        image_name = getattr(image_file, 'name', '') or ''
        identity = '{}:{}:{}'.format(
            getattr(instance, 'image_id', ''),
            image_name,
            filename,
        )
        hash = hashlib.md5(identity.encode('utf-8')).hexdigest()
    base, ext = os.path.splitext(os.path.basename(filename))
    return 'motion/%(first)s/%(second)s/%(hash)s/%(base)s%(ext)s' % {
        'first': hash[0],
        'second': hash[1],
        'hash': hash,
        'base': base or hash,
        'ext': ext or '.mp4',
    }
