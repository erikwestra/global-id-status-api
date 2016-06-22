""" statusAPI.settings

    This module defines the various settings for the statusAPI project.
"""
import os
import os.path
import sys

import dj_database_url

from statusAPI.shared.lib.settingsImporter import SettingsImporter

#############################################################################

# Calculate the absolute path to the top-level directory for our server.

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

#############################################################################

# Load our various custom settings.

import_setting = SettingsImporter(globals(),
                                  custom_settings="statusAPI.custom_settings",
                                  env_prefix="API_")

import_setting("DEBUG",                         True)
import_setting("TIME_ZONE",                     "UTC")
import_setting("SERVE_STATIC_MEDIA",            False)
# NOTE: SERVE_STATIC_MEDIA only works if DEBUG is set to True.
import_setting("DATABASE_URL",                  None)
# NOTE: DATABASE_URL uses the following general format:
#           postgres://username:password@host:port/database_name
#       or for a database on the local machine:
#           postgres://username:password@localhost/database_name
import_setting("KEEP_NONCE_VALUES_FOR", None)
# NOTE: KEEP_NONCE_VALUES_FOR is measured in days.  If this has the value
#       "none", the None values are kept forever.

#############################################################################

# Our various project settings:

# Django settings for the statusAPI project:

TEMPLATE_DEBUG = DEBUG
LANGUAGE_CODE  = 'en-us'
ALLOWED_HOSTS  = []
USE_I18N       = True
USE_L10N       = True
USE_TZ         = True
SECRET_KEY     = 'tw_0^yt2&o@028j%zlv5u9j%ai-#v7=@baxy)ww&ql(!m6d7qm'
STATIC_URL     = '/static/'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    # Enable CORS support.

    "statusAPI.middleware.cors.CORSMiddleware",
)

ROOT_URLCONF = 'statusAPI.urls'

WSGI_APPLICATION = 'statusAPI.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Install our various apps.

    'statusAPI.shared',
    'statusAPI.api',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Set up our database.

if 'test' in sys.argv:
    # Use SQLite for unit tests.
    DATABASES = {'default' : {'ENGINE' : "django.db.backends.sqlite3"}}
else:
    # Use dj_database_url to extract the database settings from the
    # DATABASE_URL setting.
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

# Configure the CORS middleware.

CORS_ALLOWED_METHODS = "POST, GET, PUT, DELETE, OPTIONS"
CORS_ALLOWED_HEADERS = "Content-Type, Authorization, Content-MD5, Nonce"
