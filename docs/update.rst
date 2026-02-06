Update from old versions
========================

0.6.x to 0.7.x
--------------

Sorry a direct upgrade is not possible, you have to install 0.7.x from scratch.


0.7.0b18 to 0.7.0b19
------------------------


::

    cd /var/www/pyscada/PyScadaServer
    sudo -u pyscada python manage.py migrate
    sudo -u pyscada python manage.py collectstatic
    sudo -u pyscada python manage.py pyscada_daemon init

0.8.x to 0.9x
-------------

Befor the Upgrade:

The folowing lines must be added to the `settings.py` after the `INSTALLED_APPS` section.

::

    pyscada = __import__("pyscada.core")
    if hasattr(pyscada.core, "additional_installed_app"):
        for app in getattr(pyscada.core, "additional_installed_app"):
            INSTALLED_APPS += [
                app,
            ]

After the Upgrade:

- Remove `"pyscada.core"`, `"pyscada.hmi"`, `"pyscada.export"` from `INSTALLED_APPS` in `settings.py`
- (optinal) choose a alternative home page by adding `PYSCADA_HOME = "/view/TEST/"` to the `settings.py`
- (optinal) add `PYSCADA_ALLOW_ANONYMOUS = True` to allow access to the pyscada hmi without login or add `PYSCADA_ALLOW_ANONYMOUS_WRITE = True` to allow write access to the pyscada hmi without login
	- Managing anonymous user display permission for IHM objects (view, page, widget, chart...) is done in the admin panel using the "Group Display Permission" -> "Unauthenticated users" configuration
- Run the folowing command in your pyscada root (where `manage.py` is located) in the pyscada venv

::

    sudo -u pyscada python manage.py migrate
    sudo -u pyscada python manage.py collectstatic
    sudo -u pyscada python manage.py pyscada_daemon init


systemd
-------


::


    sudo wget https://raw.githubusercontent.com/pyscada/PyScada/master/extras/service/systemd/pyscada_daemon.service -O /etc/systemd/system/pyscada_daemon.service
    sudo systemctl enable pyscada_daemon
    sudo systemctl disable pyscada_daq
    sudo systemctl disable pyscada_event
    sudo systemctl disable pyscada_mail
    sudo systemctl disable pyscada_export
    sudo rm /lib/systemd/system/pyscada_daq.service
    sudo rm /lib/systemd/system/pyscada_mail.service
    sudo rm /lib/systemd/system/pyscada_export.service
    sudo rm /lib/systemd/system/pyscada_event.service
    sudo systemctl daemon-reload
