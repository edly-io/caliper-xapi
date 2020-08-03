"""
A Django settings file for testing
"""

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
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'edx_analytics_transformers.django',
]

SECRET_KEY = "test_key"

LMS_ROOT_URL = 'http://localhost:18000'

RUNNING_TESTS = True
