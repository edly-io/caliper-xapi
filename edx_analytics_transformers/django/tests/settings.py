"""A Django settings file for testing"""

from __future__ import absolute_import

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

SITE_ID = 1

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
)

INSTALLED_APPS = [
    'edx_analytics_transformers.django'
]

SECRET_KEY = "test_key"

LMS_ROOT_URL = 'http://localhost:18000'
