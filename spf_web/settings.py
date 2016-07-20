"""
Django settings for spf_web project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
# Import default extensions to extend furthermore for Jinja2 and puente
from django_jinja.builtins import DEFAULT_EXTENSIONS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's_#vkn6zj^713q2x37dajjp44*mr9q**j)p!3o#z4a&jynt3-a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_jinja',
    'django_jinja.contrib._humanize',
    'puente',
    'widget_tweaks',
    'society',
    'workers',
    'events',
    'accounts',
    'invoices',
    'norlonn',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'spf_web.urls'
WSGI_APPLICATION = 'spf_web.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'en-uk'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static_files")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
MEDIA_ROOT = os.path.join(BASE_DIR, "media_files")
MEDIA_URL = "/media_files/"
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale")
]

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'DIRS': [
            os.path.join(BASE_DIR, "templates")
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'newstyle_gettext': True,
            'match_extension': '.jinja',
            'extensions': [
                'puente.ext.i18n',
            ] + DEFAULT_EXTENSIONS,
            'filters': {
                'attr': 'widget_tweaks.templatetags.widget_tweaks.set_attr'
            },
            'globals': {
                'get_language': 'django.utils.translation.get_language'
            },
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Added from old SPF
                'django.template.context_processors.request'
            ]
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates")
        ],
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                #                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                #                'django.template.context_processors.media',
                #                'django.template.context_processors.static',
                #                'django.template.context_processors.tz',
                #                'django.contrib.messages.context_processors.messages',
                #                # Added from old SPF
                #                'django.template.context_processors.request'
            ],
            'loaders': [
                # insert your TEMPLATE_LOADERS here
                'django_jinja.loaders.FileSystemLoader',
                'django_jinja.loaders.AppLoader'
            ]
        },
    },
]

PUENTE = {
    'BASE_DIR': BASE_DIR,
    'DOMAIN_METHODS': {
        'django': [
            ('**.py', 'python'),
            ('**.jinja', 'jinja2'),
            ('fjord/**/templates/**.html', 'django'),
        ],
        'djangojs': [
            ('**.js', 'javascript'),
        ]
    }
}

AUTHENTICATION_BACKENDS = ('accounts.backend.SPFBackend', 'django.contrib.auth.backends.ModelBackend',)

try:
    from spf_web.local_settings import *
except ImportError as e:
    pass
