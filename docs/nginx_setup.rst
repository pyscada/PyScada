Nginx Setup
===========


nginx configuration
-------------------


::

        sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.6.x/extras/nginx_sample.conf -O /etc/nginx/sites-available/pyscada.conf
        sudo nano /etc/nginx/sites-available/pyscada.conf
        




        
after editing, enable the configuration and restart nginx, optionaly remove the default configuration

::
        
        sudo ln -s /etc/nginx/sites-available/pyscada.conf /etc/nginx/sites-enabled/
	sudo rm /etc/nginx/sites-enabled/default


::

	sudo ln -s /etc/nginx/sites-available/pyscada.conf /etc/nginx/sites-enabled/pyscada.conf
	# SysV-Init
	sudo service nginx restart
	# systemd
	systemctl enable nginx.service # enable autostart on boot
	sudo systemctl restart nginx
