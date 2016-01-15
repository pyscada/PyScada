Installation Of A Crunchbang Based Development System
=====================================================

##1. download crunchbang (crunchbang-11-20130506-amd64.iso)
### 1.1 burn to dvd or dd to usb disk
	dd if="crunchbang-11-20130506-amd64.iso" of="/dev/sdb1"

## 2. start installation

### 2.1	Select Language
#### 2.1.1 language	
	English - English

#### 2.1.2 Country, territory or area
	other

#### 2.1.3 Continent or region
	Europe

#### 2.1.4 Country, territory or area
	Germany

### 2.2 Configure locales
	United States - en_US.UTF-8

### 2.3 Configure the keyboard
	German

### 2.4 Hostname
	faks

### 2.5 Username
	faks - default password

### 2.6 Partition disks

#### 2.6.1 
	Guided - use entire disk

#### 2.6.2
	All files in one partition

### 2.7 Install GRUB boot loader an a hard disk
	yes

## 3 Post installation script

### 3.1 update software source
	yes

### 3.2 update installed packages
	yes

### 3.3 printer support
	no

### 3.4 java support
	no

### 3.5 libreOffice
	no

### 3.6 Development packages
	yes

#### 3.6.1 version control
	yes

#### 3.6.2 open ssh server
	yes

#### 3.6.3 lamp
	no

#### 3.6.4 debian packaging 
	no

## 4 install and setup Django

### 4.1 install and setup MySql

	sudo apt-get install mysql-server mysql-workbench python-mysqldb

#### 4.1.1 set mysql admin password
	
	choose a password different from your admin pw

#### 4.1.2 create the Django/PyScada database
	
```
mysql -u root -p
enter the mysql admin pw

CREATE DATABASE FAkS_db CHARACTER SET utf8;

GRANT ALL PRIVILEGES ON FAkS_db.* TO 'FAkS-user'@'localhost' IDENTIFIED BY 'FAkS-user-password';

exit
```

### 4.2 install and setup Django

```
sudo apt-get install python-pip libhdf5-7 libhdf5-dev python-dev
cd
mkdir www
mkdir PyScadaDev
cd PyScadaDev
git clone https://github.com/trombastic/PyScada.git
cd PyScada
sudo python setup.py install
cd 
cd www
django-admin.py startproject PyScadaServer
cd PyScadaServer/
```

#### 4.2.1 settings

open settings

```
nano PyScadaServer/settings.py
```

settings.py

```
INSTALLED_APPS = (
...
	pyscada	
...
)
...
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql', 	
		'NAME': 'FAkS_db',                  	
		'USER': 'FAkS-user',                
		'PASSWORD': 'FAkS-user-password' 		
	}
}
...
STATIC_ROOT = BASE_DIR + '/static/'
```

#### 4.2.2 urls config

open urls	

```
nano PyScadaServer/urls.py
```
	
urls.py

```
urlpatterns = patterns('',
...
	url(r'^', include('pyscada.urls')),
...
)
```
	

## 5 install and setup apache 

### 5.1 install nginx and gunicorn

```
sudo apt-get install nginx
pip install gunicorn
```

### 5.2 setup gunicorn and nginx

#### 5.2.1 sync the database 

	python manage.py syncdb


#### 5.2.2 copy all static files to the local static folder

	python manage.py collectstatic


#### 5.2.3 

```
#!/bin/bash
 
NAME="PyScadaServer"                                  # Name of the application
DJANGODIR=/home/faks/www/PyScadaServer/         # Django project directory
SOCKFILE=/home/faks/www/PyScadaServer/run/gunicorn.sock  # we will communicte using this unix socket
USER=faks                                        # the user to run as
GROUP=webapps                                     # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=PyScadaServer.settings     # which settings file should Django use
DJANGO_WSGI_MODULE=PyScadaServer.wsgi             # WSGI module name
 
echo "Starting $NAME as `whoami`"
 
# Activate the virtual environment
cd $DJANGODIR
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
 
# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
 
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ../bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=debug \
  --bind=unix:$SOCKFILE

```


#### 5.2.3 edit the nginx config

```
sudo touch /etc/nginx/sites-available/pyscada-server.conf
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/pyscada-server.conf /etc/nginx/sites-enabled/pyscada-server.conf
nano /etc/nginx/sites-available/pyscada-server.conf
```

add the following lines

```
# pyscada-server.conf



```

reload nginx

```
sudo /etc/init.d/nginx reload
```

## 6 setup pyscada

### 6.1 set the configuration of field devices 

### 6.2 create and import the variables configuration



 

