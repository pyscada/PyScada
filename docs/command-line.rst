Command-line
============

Start the PyScada Daemons
-------------------------

::

	service pyscada_daemon start


::

  python manage.py PyScadaDaemonHandler daemon_name start


Start Gunicorn
--------------

::

	service gunicorn_django start


.. _sec-get-installed-pyscada-version:

Get Installed PyScada Version
---------------------------

::

	cd ~/www/PyScadaServer
	python manage.py shell
	import pyscada
	pyscada.__version__
	exit()
