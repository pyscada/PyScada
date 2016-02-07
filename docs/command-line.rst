Command-line
============

Start the PyScada Daemons
-------------------------

SysV-init and upstart:

::

	service pyscada_daemon start


systemd:

::

	systemctl start pyscada_daemon_name.service


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

	systemctl start gunicorn.service



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

	python manage.py PyScadaExportData # last 24 houres
	python manage.py PyScadaExportData "01-Mar-2015 00:00:00" # from 01. of March until now
	# from 01. of March until now, with the given filename
	python manage.py PyScadaExportData "01-Mar-2015 00:00:00" "filename.h5" 
	# from 01. of March until 10. of March, with the given filename
	python manage.py PyScadaExportData "01-Mar-2015 00:00:00" "filename.h5" "10-Mar-2015 00:00:00"