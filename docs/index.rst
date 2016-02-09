PyScada a open source SCADA system
==================================

A Open Source SCADA System with HTML5 HMI, build using the Django framework. If you like to setup your own _SCADA_ system head over to the :doc:`installation` section.


* :ref:`frontend-docs`
* :ref:`backend-docs`

.. toctree::
   :maxdepth: 2

   installation
   django_settings
   nginx_setup
   update
   command-line

.. _frontend-docs:

.. toctree::
   :maxdepth: 2
   :caption: Using the Frontend


.. _backend-docs:

.. toctree::
   :maxdepth: 2
   :caption: Using the Backend
   backend


Features
--------

- HTML5 based HMI
- Supports the following industrial Protocols
	* Modbus TCP/IP
	* Modbus RTU
	* Modbus ASCII
	* Modbus Binary
	* BACNet/IP (in development)
	* Meter-Bus, MBus (in development)
- very low Hardware requirements for the Server


Dependencies
------------

- core/HMI
	* python 2.7
	* django>=1.7
	* numpy>=1.6.0
	* pillow
	* python-daemon
- ModbusMaster
	* pymodbus>=1.2
- HDF5Export
	* h5py>=2.1.1
- SystemStatistics
	* psutil
- BACNet/IP
	* bacpypes


Contribute
----------

 - Issue Tracker: https://github.com/trombastic/PyScada/issues
 - Source Code: https://github.com/trombastic/PyScada


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.
