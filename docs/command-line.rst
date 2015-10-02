Command-line
============

Start the PyScada Daemons
-------------------------

SysV-init and upstart:

::

	service pyscada_daemon start


systemd:

::

	systemctl start pyscada_daemon.service


Django manage command:

::

  python manage.py PyScadaDaemonHandler daemon_name start


Start Gunicorn
--------------

SysV-init and upstart:

::

	service gunicorn_django start


systemd:

::

	systemctl start gunicorn_django.service



.. _sec-get-installed-pyscada-version:

Get Installed PyScada Version
---------------------------

::

	cd ~/www/PyScadaServer
	python manage.py shell
	import pyscada
	pyscada.__version__
	exit()


Export Database Tables
----------------------

::

	export_table_to_h5(TableName)
