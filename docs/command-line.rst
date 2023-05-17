Command-line
============

Restart the PyScada Daemons
---------------------------

systemd:

.. code-block:: shell

	sudo systemctl restart pyscada

Restart Gunicorn
----------------

systemd:

.. code-block:: shell

	sudo systemctl restart gunicorn.service

Restart NGINX
-------------

systemd:

.. code-block:: shell

	sudo systemctl restart nginx

Get Installed PyScada Version
-----------------------------

.. code-block:: shell

	cd /var/www/pyscada/PyScadaServer
	sudo -u pyscada python3 manage.py shell
	import pyscada
	pyscada.core.__version__
	exit()


Export Recorded Data Tables
---------------------------

.. code-block:: shell

	sudo -u pyscada python3 manage.py PyScadaExportData # last 24 houres
	sudo -u pyscada python3 manage.py PyScadaExportData --start_time "01-03-2015 00:00:00" # from 01. of March 2015 until now
	# from 01. of March until now, with the given filename
	sudo -u pyscada python3 manage.py PyScadaExportData --start_time "01-Mar-2015 00:00:00" --filename "filename.h5"
	# from 01. of March until 10. of March, with the given filename
	sudo -u pyscada python3 manage.py PyScadaExportData --start_time "01-03-2015 00:00:00" --filename "filename.h5" --stop_time "10-03-2015 00:00:00"
