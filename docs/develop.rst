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

    sudo -u pyscada -E env PATH=${PATH} pip3 install -e ./PyScada

For a plugin like PyScada-Modbus :

.. code-block:: shell

    sudo -u pyscada -E env PATH=${PATH} pip3 install -e ./PyScada-Modbus


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


Override routes
----------------

This use case is encountered when you wish to rewrite an existing view (and therefore an existing route).

The PyScada project's ``urls.py`` file is used to load the software's routes (see `here <https://docs.djangoproject.com/en/4.2/topics/http/urls/>`_).

* python virtual environment installation: located in ``/var/www/pyscada/PyScadaServer/PyScadaServer``
* Docker installation: located in ``/src/pyscada/PyScadaServer/PyScadaServer``


By default, the project's ``urls.py`` file loads only the ``urls.py`` file from ``pyscada.core``. The ``pyscada.core.urls`` file loads all the other modules ``urls.py`` files in random order.

The route used is the first valid one encountered, so if you want to replace an existing route, you have to load your route before the others, i.e. before loading ``pyscada.core.urls`` file.

To do this, you need to modify your project's ``urls.py`` file.

For a non-docker installation :

.. code-block:: shell

    sudo -u pyscada nano /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py


And include your route before pyscada.core.urls

.. code-block:: shell

    urlpatterns = [
    path('', include('pyscada.yourPlugin.urls')), #Routing file yourPlugin
    path('', include('pyscada.core.urls')),
    ]


