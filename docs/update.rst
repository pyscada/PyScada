Update/Upgrade
==============

A guide for a minor version update Pyscada 0.6.x.

Debian/Ubuntu
-------------

Stop the Daemon Processes
^^^^^^^^^^^^^^^^^^^^^^^^^

Stop all PyScada backgrounddaemon processes and guincorn.
for version 0.6.16 and newer:

::

  service pyscada_daemon stop
  service gunicorn_django stop

for update from version 0.6.15 and older. (see :ref:`sec-get-installed-pyscada-version`)

::

  cd ~/www/PyScadaServer
  python manage.py PyScadaModbusDaemon stop
  kill -TERM $(cat run/gunicorn.pid)


Update Dependencies
^^^^^^^^^^^^^^^^^^^

::

  sudo apt-get update
  sudo apt-get upgrade
  sudo pip install gunicorn --upgrade
  sudo pip install django">=1.7,<1.8" --upgrade
  sudo pip install cython --upgrade
  sudo pip install numpy --upgrade
  sudo pip install h5py --upgrade
  sudo pip install python-daemon --upgrade


Update PyScada
^^^^^^^^^^^^^^^


for the latest stable version.

::

	cd ~/
	sudo pip install git+https://github.com/trombastic/PyScada.git@stable/0.6.x

for the latest development version.

::

	cd ~/
	sudo pip install git+https://github.com/trombastic/PyScada.git@dev/0.6.x


Reinitialize Database And Update Static Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

	cd ~/www/PyScadaServer
	python manage.py migrate
	python manage.py collectstatic


Add/Update Init.d Scripts
^^^^^^^^^^^^^^^^^^^^^^^^^


To start the Dataaquasition daemon(s) and guinicorn, there are two example scripts in the git repository. Copy them to the init.d path of your machine and make them executible.

::

	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/stable/0.6.x/pyscada_daemon -O /etc/init.d/pyscada_daemon
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/stable/0.6.x/gunicorn_django -O /etc/init.d/gunicorn_django
	sudo chmod +x /etc/init.d/pyscada_daemon
	sudo chmod +x /etc/init.d/gunicorn_django


add a configuration file for every script.

::

	sudo nano /etc/default/pyscada_daemon



Fill in the full path to the django project dir (were the manage.py is located). Replace the four spaces between the daemon (modbus) and the path with a tab.

::

	#!/bin/sh
	#/etc/default/pyscada_daemon
	DAEMONS=(
		'modbus	/home/www-user/www/PyScadaServer/'
	)
	RUN_AS='www-user'


Edit the gunicorn init.d script.

::

	sudo nano /etc/default/gunicorn_django


Also fill in the path to your django project dir and replace the four spaces between the django projectname (PyScadaserver) the project path and the number of workers (10) with tabs.

::

	#!/bin/sh
	#/etc/default/gunicorn_django
	SERVERS=(
		'PyScadaServer	/home/www-user/www/PyScadaServer	10'
	)
	RUN_AS='www-user'


(optinal) install System-V style init script links

::

	sudo update-rc.d pyscada_daemon defaults
	sudo update-rc.d gunicorn_django defaults


Start the Daemon Processes
^^^^^^^^^^^^^^^^^^^^^^^^^^

Start all PyScada backgrounddaemon processes and guincorn.

::

  service pyscada_daemon start
  service gunicorn_django start
