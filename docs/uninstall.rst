Installation
============

Depending on what you need on your computer, you may NOT need to remove everything PyScada requires (such as django, mariaDB...).

PyScada
-------

  .. code-block:: shell

      # activate the PyScada virtual environment
      source /home/pyscada/.venv/bin/activate
      # uninstall PyScada
      sudo -u pyscada -E env PATH=${PATH} pip3 uninstall pyscada
      # clean static files
      python /var/www/pyscada/PyScadaServer/manage.py collectstatic --clear --no-input
      # drop the mariaDB database, by default called PyScada_db
      sudo  mysql -u PyScada-user -p -e "DROP DATABASE IF EXISTS database_name PyScada_db;"

Uninstall prerequisites (IMPORTANT: only if not needed by other software !)

  .. code-block:: shell

      # Uninstall prerequisites
      DEB_TO_UNINSTALL="
        libatlas-base-dev
        libffi-dev
        libhdf5-103
        libhdf5-dev
        libjpeg-dev
        libmariadb-dev
        libopenjp2-7
        mariadb-server
        nginx
        python3-dev
        python3-mysqldb
        python3-pip
        python3-venv
        zlib1g-dev
        pkg-config
      "
      sudo apt remove -y $DEB_TO_UNINSTALL

      PIP_TO_UNINSTALL="
        cffi
        Cython
        docutils
        gunicorn
        lxml
        mysqlclient
        numpy
      "
      sudo -u pyscada -E env PATH=${PATH} pip3 uninstall $PIP_TO_UNINSTALL

PyScada plugin
--------------

  .. code-block:: shell

      # activate the PyScada virtual environment
      source /home/pyscada/.venv/bin/activate
      # uninstall PyScada-Plugin
      sudo -u pyscada -E env PATH=${PATH} pip3 uninstall pyscada-plugin
      # clean static files
      python /var/www/pyscada/PyScadaServer/manage.py collectstatic --clear --no-input
      python /var/www/pyscada/PyScadaServer/manage.py collectstatic --no-input
      # clean db, may depend on the plugin
      python /var/www/pyscada/PyScadaServer/manage.py migrate pyscada-plugin zero

Depending on the plugin, you may need to uninstall some packages.
