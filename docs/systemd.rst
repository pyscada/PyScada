Add Init.d Scripts for systemd (optional)
-----------------------------------------

Download the sample Unit-Files for systemd.

::

    sudo -i
    wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/pyscada_daq.service -O /lib/systemd/system/pyscada_daq.service
    wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/pyscada_event.service -O /lib/systemd/system/pyscada_event.service
    wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/pyscada_mail.service -O /lib/systemd/system/pyscada_mail.service
    wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/pyscada_export.service -O /lib/systemd/system/pyscada_export.service
    wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/gunicorn.socket -O /lib/systemd/system/gunicorn.socket
    wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/gunicorn.service -O /lib/systemd/system/gunicorn.service
    
    # enable the services for autostart
    systemctl enable gunicorn
    systemctl enable pyscada_daq
    systemctl enable pyscada_event
    systemctl enable pyscada_mail
    systemctl enable pyscada_export


Start gunicorn and all PyScada services

::

    sudo systemctl start gunicorn
    sudo systemctl start pyscada_daq
    sudo systemctl start pyscada_event
    sudo systemctl start pyscada_mail
    sudo systemctl start pyscada_export
