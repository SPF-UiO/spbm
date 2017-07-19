"""
Django settings for spf_web project.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

"""
SPBM-related settings
"""
SPBM = {
    'dates': {
        'invoicing': 15,
        'deadline': 10,
        'wages': 25,
    }
}

import os

# We need the default extensions
from django_jinja.builtins import DEFAULT_EXTENSIONS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's_#vkn6zj^713q2x37dajjp44*mr9q**j)p!3o#z4a&jynt3-a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# When Debug is False, ALLOWED_HOSTS must be configured correctly.
ALLOWED_HOSTS = []
INTERNAL_IPS = ['127.0.0.1']
ROOT_URLCONF = 'spbm.urls'
WSGI_APPLICATION = 'spbm.wsgi.application'

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
    'spbm.apps.society',
    'spbm.apps.accounts',
    'spbm.apps.norlonn',
    'debug_toolbar'
)

# Middleware onion layers
# https://docs.djangoproject.com/en/1.10/topics/http/middleware/
MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware'
)

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
LANGUAGE_CODE = 'en-uk'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static_files")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
MEDIA_ROOT = os.path.join(BASE_DIR, "media_files")
MEDIA_URL = "/media_files/"
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale")
]
# Template providers, as well as filters and more
# https://docs.djangoproject.com/en/1.10/topics/templates/#configuration
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
            'extensions': DEFAULT_EXTENSIONS + [
                              'puente.ext.i18n',
                          ],
            'filters': {
                'attr': 'widget_tweaks.templatetags.widget_tweaks.set_attr',
                'localize': 'django.utils.formats.localize',
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
            ]
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Useful to overwrite, say, django.contrib.admin templates
            os.path.join(BASE_DIR, "templates")
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Provided to support django.contrib.admin
                'django.contrib.auth.context_processors.auth',
            ],
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
        # Feel free to uncomment once there's any JavaScript with i18n.
        # 'djangojs': [
        #     ('**.js', 'javascript'),
        # ]
    }
}

AUTHENTICATION_BACKENDS = ('spbm.apps.accounts.backend.SPFBackend', 'django.contrib.auth.backends.ModelBackend',)

try:
    from spbm.local_settings import *
except ImportError as e:
    pass
