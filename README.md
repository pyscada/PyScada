PyScada
=======

A Open Source SCADA System with HTML5 HMI, build using the Django framework.


Features
--------

* HTML5 based HMI
* Supports the following industrial Protocols
	- Modbus TCP/IP
	- Modbus RTU (in development)
	- Modbus ASCII (in development)
	- BACNet IP (in development)
	- Meter-Bus, MBus (in development)
* very low Hardware requirements for the Server


Dependencies
------------

* Python 2.7
* django 1.6
* pymodbus>=1.2
* numpy>=1.6.0
* h5py>=2.1.1
* pillow

Quick Start
-----------

## download PyScada ##

```

```


## new Django project ##

start a new Django project

```
cd ~/www
django-admin.py startproject PyScadaServer
cd PySadaServer
```

## setup the MySql ##

create a new database (PyScada_db) for PyScada, add a new user and grand the necessary rights

```
mysql -u root -p -e "CREATE DATABASE PyScada_db CHARACTER SET utf8; GRANT ALL PRIVILEGES ON PyScada_db.* TO 'PSS-user'@'localhost' IDENTIFIED BY 'PySadaServer-user-password';"
``` 

## Django settings ##


Add the PyScada apps to the INSTALLED_APPS list in the Django settings file.

```
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pyscada',
    'pyscada.hmi',
    'pyscada.modbus',
)
```

adjust the database settings

```
'default': {
        'ENGINE': 'django.db.backends.mysql',   
        'NAME': 'PyScada_db',                      
        'USER': 'PSS-user',                
        'PASSWORD': 'PySadaServer-user-password'        
    }
```

and add the following PyScada specific parameters to your settings (PySadaServer/settings.py) file.


```
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
```

urls.py

```
urlpatterns = patterns('',
...
    url(r'^', include('pyscada.urls')),
...
)
```


## setup PyScadaServer ##

```
python manage.py migrate
python manage.py collectstatic
```

