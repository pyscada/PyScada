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
* very low Hardware requirements for the Server


Dependencies
------------

* Python 2.7
* django 1.6
* pymodbus>=1.2
* numpy>=1.6.0
* h5py>=2.1.1


Quick Start
-----------



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

and add the following PyScada specific parameters to your settings file.


```
# PyScada settings
# https://github.com/trombastic/PyScada

# folder were the daemon pid files are stored
PID_ROOT = BASE_DIR + '/run/'

# list of available client Protocols
# 
PYSCADA_CLIENTS = (
	('modbus','Modbus Client',),
)

# parameters for the Modbus Client
# 	polling_interval 	how often the modbus client requests data
#						from devices and write to the cache
#
#	recording_intervall	how often the data is written to the database
#
# 	pid_file			file were the daemon pid is stored

PYSCADA_MODBUS = {
	'polling_interval':1,
	'recording_intervall':5,
	'pid_file_name': 'daemon-modbus.pid'
}

```






