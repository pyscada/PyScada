Nginx Setup
===========


nginx configuration
-------------------


::
        
        # debian
        sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/nginx_sample.conf -O /etc/nginx/sites-available/pyscada.conf
        sudo nano /etc/nginx/sites-available/pyscada.conf
        # Fedora
        sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/nginx_sample.conf -O /etc/nginx/conf.d/pyscada.conf
        sudo nano /etc/nginx/conf.d/pyscada.conf


after editing, enable the configuration and restart nginx, optionaly remove the default configuration

::

        # debian
        sudo ln -s /etc/nginx/sites-available/pyscada.conf /etc/nginx/sites-enabled/
        sudo rm /etc/nginx/sites-enabled/default



to use ssl
----------

generate ssl certificates.



::

        # for Debian, Ubuntu, Raspian
        sudo mkdir /etc/nginx/ssl
        # the certificate will be valid for 5 Years,
        sudo openssl req -x509 -nodes -days 1780 -newkey rsa:2048 -keyout /etc/nginx/ssl/pyscada_server.key -out /etc/nginx/ssl/pyscada_server.crt





now it's time to [re]start nginx.


::


        # SysV-Init
        sudo service nginx restart
        # systemd
        systemctl enable nginx.service # enable autostart on boot
        sudo systemctl restart nginx


for Fedora you have to allow nginx to serve the static and media folder.

::
        
        sudo chcon -Rt httpd_sys_content_t /var/www/pyscada/http/