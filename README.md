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
* django>=1.6
* pymodbus>=1.2
* numpy>=1.6.0
* h5py>=2.1.1
* pillow
* psutil

Quick Start
-----------

## download and build PyScada ##

first download and build PyScada.

```
git clone https://github.com/trombastic/PyScada.git
git checkout dev/0.7.x
python setup.py install
```


## setup a new Pyscada Server instance ##

to setup a new Pyscada Server instance start a Django project

```
cd ~/www
django-admin.py startproject PyScadaServer
cd PySadaServer
```

### setup the MySql ###

create a new database (PyScada_db) for PyScada, add a new user and grand the necessary rights

```
mysql -u root -p -e "CREATE DATABASE PyScada_db CHARACTER SET utf8; GRANT ALL PRIVILEGES ON PyScada_db.* TO 'PSS-user'@'localhost' IDENTIFIED BY 'PySadaServer-user-password';"
``` 

### Django settings ###


Add the PyScada apps to the INSTALLED_APPS list in the Django settings file (`PyScadaServer/settings.py`). 

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

adjust the database settings section.

```
'default': {
        'ENGINE': 'django.db.backends.mysql',   
        'NAME': 'PyScada_db',                      
        'USER': 'PSS-user',                
        'PASSWORD': 'PySadaServer-user-password'        
    }
```

and add the following PyScada specific parameters to Djago settings file.


```
STATIC_ROOT = BASE_DIR + '/static/'

# PyScada settings
# https://github.com/trombastic/PyScada

# folder were the daemon pid files are stored
PID_ROOT = BASE_DIR + '/run/'


# global pyscada settings
#
#	cache_timeout 			timeperiode that is stored in the round robin 
#							cache table in minutes  
#   

PYSCADA = {
    'cache_timeout':1440,
        }

# list of available client Protocols
# 
PYSCADA_CLIENTS = (
    ('modbus','Modbus Client',),
)

# parameters for the Modbus Client
#
# 	polling_interval 		how often the modbus client requests data
#							from devices and write to the cache in seconds
#

PYSCADA_MODBUS = {
    'polling_interval':5,
}

# parameters for the Modbus Client
#
#   recording_interval          time distance in seconds between two 
#								values in the backup file
#   write_to_file_interval      time in minutes to write the cache data 
#								to the export file  
#           
#   backup_path                 path were the backup files are stored
#   
#   backup_filename_prefix      filename prefix for the backup files
#
#
         
PYSCADA_EXPORT = {
    'recording_interval':5, 
    'write_to_file_interval':30,
    'backup_path':'~/measurement_data_dumps',
    'backup_filename_prefix':'TUKT_measurement_data'
}
```

add the folowing line to `PyScadaServer/urls.py`

```
urlpatterns = patterns('',
...
    url(r'^', include('pyscada.urls')),
...
)
```


### setup PyScadaServer ###

```
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

## start the daemon processes ##

```

```

