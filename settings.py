# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Initialize App Engine and import the default settings (DB backend, etc.).
# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file.
from djangoappengine.settings_base import *

import os
from djangoappengine.utils import on_production_server

# Activate django-dbindexer for the default database
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': DATABASES['default']}
AUTOLOAD_SITECONF = 'indexes'

JAVASCRIPT_TRANSLATION_VERSION = 1

SECRET_KEY = '[Complete_SECRET_KEY]'

ALLOWED_HOSTS = ['.contenbox.appspot.com']

AUTHENTICATION_BACKENDS = (
   'social.backends.google.GoogleOAuth2',
   'permission_backend_nonrel.backends.NonrelPermissionBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['https://www.googleapis.com/auth/userinfo.email',
                                 'https://www.googleapis.com/auth/userinfo.profile',
                                 'https://www.googleapis.com/auth/drive.readonly',]

LOGIN_URL = '/login/google-oauth2/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_ADMIN = '/admin/'
SOCIAL_AUTH_USE_AS_ADMIN_LOGIN = True

SOCIAL_AUTH_STRATEGY = "social.strategies.django_globalconfig_strategy.DjangoGlobalConfigStrategy"

from django.utils.translation import ugettext_lazy as _

LANGUAGES = (
    ('en', _('English')),
    ('es', _('Spanish')),
    ('pt', _('Portuguese')),
)

GET_SOLO_TEMPLATE_TAG_NAME = 'get_config'
SOLO_CACHE = 'default'

SUMMERNOTE_CONFIG = {
    # Change editor size
    'width': '600',
    'height': '400',

    # Customize toolbar buttons
    'toolbar': [
        ['style', ['bold', 'italic', 'underline', 'clear']],
        ['fontsize', ['fontsize']],
        ['para', ['ul', 'ol', 'paragraph']],
        ['insert', ['link']],
    ],
}


INSTALLED_APPS = (
    'yawdadmin',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangotoolbox',
    'autoload',
    'dbindexer',
    'filetransfers',
    'permission_backend_nonrel',
    'adminoauthlogin',

    'modeltranslation',
    'django_summernote',
    'social.apps.django_app.default',
    'solo',
    'search',
    'django_ajax',

    'main',
    'invitations',
    'help',
    'config',

    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
)

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',

    'django.middleware.cache.UpdateCacheMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',
)


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'TIMEOUT': 0,
    },
    'dev': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

if on_production_server:
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = 60
else:
    CACHE_MIDDLEWARE_ALIAS = 'dev'
    CACHE_MIDDLEWARE_SECONDS = 0

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

ADMIN_MEDIA_PREFIX = '/media/admin/'
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

STATIC_URL = '/static/'
STATIC_ROOT = 'static/'

ROOT_URLCONF = 'urls'


ADMIN_SITE_NAME = 'Content Box'
ADMIN_SITE_DESCRIPTION = None