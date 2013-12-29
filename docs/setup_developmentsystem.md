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
	
	´´´
	mysql -u root -p
	enter the mysql admin pw
	
	CREATE DATABASE FAkS_db CHARACTER SET utf8;
	
	GRANT ALL PRIVILEGES ON FAkS_db.* TO 'FAkS-user'@'localhost' IDENTIFIED BY 'FAkS-user-password';
	
	exit
	´´´

### 4.2 install and setup Django

	sudo install python-pip



 

