To start the Dataaquasition daemon(s) and guinicorn, there are two example scripts in the git repository. Copy them to the init.d path of your machine and make them executible.

::

	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/SysV-init/pyscada_daemon -O /etc/init.d/pyscada_daemon
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/SysV-init/gunicorn_django -O /etc/init.d/gunicorn_django

	sudo chmod +x /etc/init.d/pyscada_daemon
	sudo chmod +x /etc/init.d/gunicorn_django


add a configuration file for every script.

::

	sudo nano /etc/default/pyscada_daemon



Fill in the full path to the django project dir (were the manage.py is located).

::

	#!/bin/sh
	#/etc/default/pyscada_daemon
	DJANGODIR='/var/www/pyscada/PyScadaServer/'
	RUN_AS='pyscada'


Edit configuratio for the gunicorn init.d script.

::

	sudo nano /etc/default/gunicorn_django


Also fill in the path to your django project dir and replace the four spaces between the django projectname (PyScadaserver) the project path and the number of workers (10) with tabs.

::

	#!/bin/sh
	#/etc/default/gunicorn_django
	SERVERS=(
		'PyScadaServer	/var/www/pyscada/PyScadaServer	5'
	)
	RUN_AS='pyscada'


(optinal) install System-V style init script links.

::

	sudo update-rc.d pyscada_daemon defaults
	sudo update-rc.d gunicorn_django defaults


Start gunicorn and all PyScada services

::

	sudo service gunicorn_django start
	sudo service pyscada_daemon