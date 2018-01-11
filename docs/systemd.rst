Add Init.d Scripts for systemd (optional)
-----------------------------------------

Download the sample Unit-Files for systemd.

::

    sudo -i
    wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/pyscada_daemon.service -O /etc/systemd/system/pyscada_daemon.service
    wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/gunicorn.socket -O /etc/systemd/system/gunicorn.socket
    wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/gunicorn.service -O /etc/systemd/system/gunicorn.service
    
    # enable the services for autostart
    systemctl enable gunicorn
    systemctl enable pyscada_daemon


Start gunicorn and all PyScada services

::

    sudo systemctl start gunicorn
    sudo systemctl start pyscada_daemon

