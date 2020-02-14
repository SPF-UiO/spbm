"""
Django settings for SPBM project.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

"""
SPBM-related settings
"""
SPBM = {
    'dates': {
        'invoicing': 15,
        'deadline': 10,
        'wages': 25,
    },
    'fee': 0.3,
}

import os
import ast

# We need the default extensions
from django_jinja.builtins import DEFAULT_EXTENSIONS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Environment specific settings
################################################################################

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("SPBM_DEBUG", default=0))

# SECURITY WARNING: When Debug is False, ALLOWED_HOSTS must be configured 
# correctly.
ALLOWED_HOSTS = os.environ.get("SPBM_ALLOWED_HOSTS", default="").split(",")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Note to self: this is overriden using local_settings.py, but may be moved 
#               into the Docker container instead
SECRET_KEY = os.environ.get("SPBM_SECRET_KEY", default='s_#vkn6zj^713q2x37dajjp44*mr9q**j)p!3o#z4a&jynt3-a')

# SECURITY WARNING: Enables debug toolbar if debug is enabled.
DEBUG_TOOLBAR_CONFIG = {
    # Per the source this only checks for REMOTE_ADDR matching INTERNAL_IPS,
    # followed by checking DEBUG. As we want to ignore the IPS and show it if
    # DEBUG is enabled, we replace it with the value of DEBUG.
    # https://github.com/recamshak/django-debug-panel/blob/master/debug_panel/middleware.py#L15
    "SHOW_TOOLBAR_CALLBACK": lambda _: bool(DEBUG)
}

# SECURITY WARNING: Prevents other hosts from making unsafe requests.
CSRF_TRUSTED_ORIGINS = os.environ.get("SPBM_CSRF_TRUSTED_ORIGINS", default='').split(",")

# Database
# https://docs.djangoproject.com/en/dev/ref/databases/
DATABASES = {
    'default': {
        'ENGINE': os.environ.get("SPBM_DB_ENGINE", default='django.db.backends.sqlite3'),
        'NAME': os.environ.get("SPBM_DB_NAME", default=os.path.join(BASE_DIR, 'db.sqlite3')),
        'HOST': os.environ.get("SPBM_DB_HOST", default=None),
        'PORT': os.environ.get("SPBM_DB_PORT", default=None),
        'USER': os.environ.get("SPBM_DB_USER", default=None),
        'PASSWORD': os.environ.get("SPBM_DB_PASSWORD", default=None),
    }
}

# Application related settings
################################################################################
ROOT_URLCONF = 'spbm.urls'
WSGI_APPLICATION = 'spbm.wsgi.application'

CSRF_COOKIE_SECURE = ast.literal_eval(os.environ.get("SPBM_CSRF_COOKIE_SECURE", default='True'))
SESSION_COOKIE_SECURE = ast.literal_eval(os.environ.get("SPBM_SESSION_COOKIE_SECURE", default='True'))

X_FRAME_OPTIONS = 'DENY'

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
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware'
)


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
LANGUAGE_CODE = 'en-gb'
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
                'django.contrib.messages.context_processors.messages',
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
