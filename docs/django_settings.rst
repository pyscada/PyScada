Django Settings
===============


urls.py
-------


Open the urls configuration file and add the necessary rewrite rule to the django URL dispatcher.

::

    nano /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py


::

    ...
    from django.conf.urls import url, include
    from django.contrib import admin

    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'^', include('pyscada.hmi.urls')),
    ]
    ...



settings.py
-----------


Open the django settings file and make the following modifications. See also the `django documentation <https://docs.djangoproject.com/en/1.8/ref/settings/>`_ for more Information.

::

    nano /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py


First deactivate the debugging, if debugging is active django will keep all SQL queries in the ram, the data-acquisition
runs a massive amount of queries so your system will run fast out of memory. Keep in mind to restart gunicorn and the
pysada daemons after you change the debugging state.

::

    DEBUG = False


Add the host/domain of your machine, in this case every url that point to a ip of the machine is allowed.

::

    ALLOWED_HOSTS = ['*']


Add PyScada and the PyScada sub-apps to the installed apps list of Django.

::

    INSTALLED_APPS = [
        ...
        'pyscada.core',
        'pyscada.modbus',
        'pyscada.phant',
        'pyscada.visa',
        'pyscada.hmi',
        'pyscada.systemstat',
        'pyscada.export',
        'pyscada.onewire',
        'pyscada.smbus',
    ]

To use the MySQL Database, fill in the database, the user and password as selected in the *create Database section*.

::

    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.mysql',
            'NAME':     'PyScada_db',
            'USER':     'PyScada-user',
            'PASSWORD': 'PyScada-user-password',
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }


Set the static file and media dir as follows.

::

    ...
    STATIC_URL = '/static/'

    STATIC_ROOT = '/var/www/pyscada/http/static/'

    MEDIA_URL = '/media/'

    MEDIA_ROOT = '/var/www/pyscada/http/media/'


Add all PyScada specific settings, keep in mind to set the file right file encoding in the `settings.py` file header (see also https://www.python.org/dev/peps/pep-0263/).

::

    #!/usr/bin/python
    # -*- coding: <encoding name> -*-


Append to the end of the `settings.py`:

::

    # PyScada settings
    # https://github.com/trombastic/PyScada

    # email settings
    DEFAULT_FROM_EMAIL = 'example@host.com'
    EMAIL_HOST = 'mail.host.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'pyscada@host.com'
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    EMAIL_HOST_PASSWORD = 'password'
    EMAIL_PREFIX = 'PREFIX' # Mail subject will be "PREFIX subjecttext"

    # meta information's about the plant site
    PYSCADA_META = {
        'name':'A SHORT NAME',
        'description':'A SHORT DESCRIPTION',
    }

    # export properties
    #
    PYSCADA_EXPORT = {
        'file_prefix':'PREFIX_',
        'output_folder':'~/measurement_data_dumps',
    }
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': BASE_DIR + '/pyscada_debug.log',
                'formatter': 'standard',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
            'pyscada': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
