Using the Front-End
===================

The ``settings.py`` file is usually located in ``/var/www/pyscada/PyScadaServer/PyScadaServer/``.

The home page can be defined to be a specific view in the ``settings.py`` file using:

  .. code-block::

      PYSCADA_HOME = "/view/TEST/"

Allowing anonymous access permission is defined in the ``settings.py`` file using:

  .. code-block::

      PYSCADA_ALLOW_ANONYMOUS = True
      PYSCADA_ALLOW_ANONYMOUS_WRITE = True
