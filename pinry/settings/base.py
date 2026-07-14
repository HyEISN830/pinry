import os

from django.contrib.messages import constants as messages


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _env_tuple(name, default=''):
    return tuple(
        value.strip()
        for value in os.environ.get(name, default).split(',')
        if value.strip()
    )


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _env_int(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'taggit',
    'compressor',
    'django_images',
    'core',
    'users',
    'pinry_plugins.apps.PinryPluginsConfig',
]

ROOT_URLCONF = 'pinry.urls'

MIDDLEWARE = [

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pinry.middleware.ForceCSRFCookieMiddleware',
    'users.middleware.Public',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'pinry/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.template_settings',
            ],
        },
    },
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'pinry/static')]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/data/media')
TRUSTED_PROXY_IPS = _env_tuple('TRUSTED_PROXY_IPS')

IMAGE_FETCH_ASYNC_ENABLED = _env_bool('IMAGE_FETCH_ASYNC_ENABLED', False)
IMAGE_FETCH_WORKER_IDLE_SECONDS = _env_int('IMAGE_FETCH_WORKER_IDLE_SECONDS', 5)
IMAGE_FETCH_PROCESSING_TIMEOUT_SECONDS = _env_int(
    'IMAGE_FETCH_PROCESSING_TIMEOUT_SECONDS',
    900,
)
IMAGE_FETCH_DB_LOCK_BACKOFF_SECONDS = _env_int(
    'IMAGE_FETCH_DB_LOCK_BACKOFF_SECONDS',
    2,
)

WSGI_APPLICATION = 'pinry.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

# Set to False to disable people from creating new accounts.
ALLOW_NEW_REGISTRATIONS = False

# Set to False to force users to login before seeing any pins.
PUBLIC = True

AUTHENTICATION_BACKENDS = [
    'users.auth.backends.CombinedAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/'

SESSION_COOKIE_AGE = 12 * 60 * 60

MESSAGE_TAGS = {
    messages.WARNING: 'alert alert-warning',
    messages.ERROR: 'alert alert-danger',
    messages.SUCCESS: 'alert alert-success',
    messages.INFO: 'alert alert-info',
}

API_LIMIT_PER_PAGE = 50

IMAGE_PATH = 'core.utils.upload_path'

IMAGE_SIZES = {
    'thumbnail': {'size': [240, 0]},
    'standard': {'size': [600, 0]},
    'square': {'crop': True, 'size': [125, 125]},
}

IMAGE_PREVIEW_THROTTLE_BYTES_PER_SECOND = 1024 * 1024
IMAGE_UPLOAD_THROTTLE_BYTES_PER_SECOND = 1024 * 1024

FILE_UPLOAD_HANDLERS = [
    'pinry.upload_handlers.ThrottledTemporaryFileUploadHandler',
]

ANIMATED_GIF_THUMBNAIL_SIZE = 'animated_thumbnail_fast'
ANIMATED_GIF_THUMBNAIL_OPTIONS = {
    'size': [180, 0],
    'max_frames': 48,
}

AVATAR_MAX_UPLOAD_SIZE = 2 * 1024 * 1024

AVATAR_SIZES = {
    'small': {'crop': True, 'size': [30, 30], 'upscale': True},
    'medium': {'crop': True, 'size': [48, 48], 'upscale': True},
    'large': {'crop': True, 'size': [96, 96], 'upscale': True},
}

# IS_TEST is a variable to mark if the test is running
IS_TEST = False

# User custom settings
IMAGE_AUTO_DELETE = True

# Rest Framework

DRF_URL_FIELD_NAME = "resource_link"

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'URL_FIELD_NAME': DRF_URL_FIELD_NAME,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': API_LIMIT_PER_PAGE,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'likes_minute': '30/min',
        'likes_day': '300/day',
    },
}
