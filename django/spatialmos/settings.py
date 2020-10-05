"""Django settings for spatialmos project. Generated in django Version 3.0.3."""

import os
import environ

# Import Environ
env = environ.Env(
    # set casting, default value
    ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost']),
    DEBUG=(bool, False),
    DB=(str, 'postgres'),
    POSTGRES_HOST=(str, 'postgres'),
    POSTGRES_USER=(str, 'postgres'),
    POSTGRES_PASSWORD=(str, 'postgres'),
    SECRET_KEY=(str, 'jd3jqb@r1jaaj^(2e&$qam8#fbp)6qqu+9cz8u^u+4)%scl^f#'),
    LASTCOMMIT=(str, 'LASTCOMMIT'),
    UPDATETIME=(str, 'UPDATETIME')
)
environ.Env.read_env()

# The last commit ist displayed in the /systemstatus
LASTCOMMIT = env('LASTCOMMIT')

# Display the updatetime in the /systemstatus
UPDATETIME = env('UPDATETIME')

# Basic settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')


# Application
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # django-cleanup
    'django_cleanup.apps.CleanupConfig',

    # django rest framework
    'rest_framework',

    # spatialMOS app
    'predictions.apps.PredictionsConfig',
    'pages.apps.PagesConfig',
    'api.apps.ApiConfig',
    'statusfiles.apps.StatusfilesConfig',
]

# Django Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL-root-config
ROOT_URLCONF = 'spatialmos.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'spatialmos/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'spatialmos.context_processors.custom_context'
            ],
        },
    },
]

# WSGI module
WSGI_APPLICATION = 'spatialmos.wsgi.application'


# Database connection
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': 5432,
    }
}


# Password validation
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

# Django REST framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

# HTTPS Support 
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Language and Time Zones
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Vienna'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static and Media files (CSS, JavaScript, Images)
MEDIA_URL = '/media/'
MEDIA_ROOT = '/www/media/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_URL = '/static/'
STATIC_ROOT = '/www/static/'
