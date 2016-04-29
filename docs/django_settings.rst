Django Settings
===============


urls.py
-------


Open the urls configuration file and add the nesseary rewrite rule to the django URL dispatcher.

::

	nano /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py


::

	...
		url(r'^admin/', include(admin.site.urls)),
		url(r'^', include('pyscada.hmi.urls')),
	...

	

settings.py
-----------


Open the django settings file and make the following modifications. See also the `django documentation <https://docs.djangoproject.com/en/1.8/ref/settings/>`_ for more Information.

::

	nano /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py


First deaktivate the debuging, if debuging is active django will keep all SQL queries in the ram, the dataaquasition runs many queries so your system will run fast out of memory. Keep in mind to restart guinicorn and all dataaquasion daemons after you change the debuging state.

::

	DEBUG = False
	TEMPLATE_DEBUG = DEBUG


Add the host/domain of your machine, is this case every url that point to a ip of the machine is allowed.

::

	ALLOWED_HOSTS = ['*']


Add the PyScada and the subapps to the installed apps list.

::

	INSTALLED_APPS = (
		...
		'pyscada',
		'pyscada.modbus',
		'pyscada.hmi',
		'pyscada.systemstat',
		'pyscada.export'
	)

To use the MySQL Database, fill in the database, the user and password as selected in the *create Database section*.

::

	DATABASES = {
		'default': {
			'ENGINE':   'django.db.backends.mysql',
			'NAME':     'PyScada_db',
			'USER':     'PyScada-user',
			'PASSWORD': 'PyScada-user-password'
		}
	}


Set the static file and media dir as followes.

::

	...
	# Static files (CSS, JavaScript, Images)
	# https://docs.djangoproject.com/en/1.6/howto/static-files/

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
	
	# meta informations about the plant site 
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
