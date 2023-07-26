.. IMPORTANT::
    To use PyScada in developer mode, you should install it using the `pip editable mode (-e) <https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e>`_

For developers
==============

Activate PyScada virtual environment
------------------------------------

.. code-block:: shell

    source /home/pyscada/.venv/bin/activate


Cloning the repository
----------------------

.. code-block:: shell

    git clone git@github.com:pyscada/PyScada.git

For a plugin like PyScada-Modbus :

.. code-block:: shell

    git clone git@github.com:pyscada/PyScada-Modbus.git


Pip editable installation
-------------------------

After activating the virtual environment :

.. code-block:: shell

    sudo -E env PATH=${PATH} pip3 install -e ./PyScada

For a plugin like PyScada-Modbus :

.. code-block:: shell

    sudo -E env PATH=${PATH} pip3 install -e ./PyScada-Modbus


Restarting the application
--------------------------

After activating the virtual environment, to apply you changes, depending on them, may need to :

create migrations

.. code-block:: shell

    python3 /var/www/pyscada/PyScadaServer/manage.py makemigrations

apply them

.. code-block:: shell

    python3 /var/www/pyscada/PyScadaServer/manage.py migrate

copy static files (answer yes).

.. code-block:: shell

    sudo -u pyscada -E env PATH=${PATH} python3 /var/www/pyscada/PyScadaServer/manage.py collectstatic

Then you can :

For urls, views or admin changes, restart gunicorn.

.. code-block:: shell

    sudo systemctl restart gunicorn

Otherwise restart PyScada.

.. code-block:: shell

    sudo systemctl restart pyscada
