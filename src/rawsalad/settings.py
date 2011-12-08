import os
ROOT_PATH = os.path.dirname( __file__ )

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Bartosz Stalewski', 'bartekstalewski@gmail.com'),
    ('Krzysztof Trzewiczek', 'ktrzewiczek@centrumcyfrowe.pl'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': '', 
        'USER': '',
        'PASSWORD': '',
        'HOST': '',    
        'PORT': '',    
    }
}

TIME_ZONE = 'Europe/Warsaw'
LANGUAGE_CODE = 'pl'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_PREFIX = ''
MEDIA_ROOT = os.path.join( ROOT_PATH, 'site_media/' )
MEDIA_URL = 'http://127.0.0.1:8000/site_media/' # for development period
ADMIN_MEDIA_PREFIX = '/admin_media/'

SECRET_KEY = '%f(004sk%!4d*xr$nu6=_5mn_jl6t@2j(jh+wc7#r8o2ttfyev'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'rawsalad.urls'

TEMPLATE_DIRS = (
    os.path.join( ROOT_PATH, 'templates' ),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'rawsalad.databrowser',
    'rawsalad.papi',
)
