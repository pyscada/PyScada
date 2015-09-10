"""
Django settings for PyScadaServer project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'la!=&&zj_&7)!ij9(8ncwull2-x@y_edi80@zs6uca9x+659jc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'pyscada',
	'pyscada.modbus',
	'pyscada.hmi',
	'pyscada.systemstat'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'PyScadaServer.urls'

WSGI_APPLICATION = 'PyScadaServer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'faks_db',
        'USER': 'FAkS-user',
        'PASSWORD':'FAkS-user-password'

    }
}
"""
# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR + '/static/'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR + '/media/'

# PyScada settings
# https://github.com/trombastic/PyScada

# folder were the daemon pid files are stored
PID_ROOT = BASE_DIR + '/run/'

# list of available client Protocols
#
PYSCADA_CLIENTS = (
	('modbus','Modbus Client',),
	('systemstat','Monitor Local System',),
)

# parameters for the Modbus Client
# 	polling_interval 	how often the modbus client requests data
#						from devices and write to the cache
#
#	recording_intervall how often the data is written to the database
#
# 	pid_file			file were the daemon pid is stored

PYSCADA_MODBUS = {
	'polling_interval':5,
	'recording_interval':5,
	'pid_file_name': 'daemon-modbus.pid'
}

PYSCADA_SYSTEMSTAT = {
	'polling_interval':5,
	'recording_interval':5,
	'pid_file_name': 'daemon-sysstat.pid'
}
