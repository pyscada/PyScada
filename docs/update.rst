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
