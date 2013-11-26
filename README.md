PyScada
=======

An Python, Django, ExtJS based Open Source Scada System


# dependencies
## Python
* Python 2.7.3
* easy_install
* pip
* django > 1.4
* pymodbus 
* twisted 
* pyserial
* zope.interface
* scipy
* numpy
* mysqldb
## other
* Mysql Server
# Installation
## Ubuntu

## setup mysql server
login to the mysql shell, use the password you set during the installation of mysql

```
mysql -u root -p
enter Password:
```

create a new database

```
CREATE DATABASE FAkS_db CHARACTER SET utf8;
```

add a new user for Django and grand him all privileges for the database

```
#!bash
GRANT ALL PRIVILEGES ON FAkS_db.* TO 'FAkS-user'@'localhost' IDENTIFIED BY 'FAkS-user-password';
```
leave the mysql shell

```
exit
```

## setup django environment

init the project folder

```
django-admin.py startproject PyScadaServer
```

```
cd PyScadaServer/PyScadaServer
nano settings.py
```




setup django for the first use, you have to specify a username and a password for admin user to log into the admin webpage.


```
python manage.py syncdb 
```

