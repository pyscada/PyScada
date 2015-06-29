PyScada a open source SCADA system
==================================

A Open Source SCADA System with HTML5 HMI, build using the Django framework.

The main documentation for the site is organized into a couple sections:

* :ref:`install-docs`
* :ref:`frontend-docs`
* :ref:`backend-docs`


.. _install-docs:

.. toctree::
   :maxdepth: 2
   :caption: How to Install

   debian_like_systems
   raspberry_pi


.. _frontend-docs:

.. toctree::
   :maxdepth: 2
   :caption: Using the Frontend


.. _backend-docs:

.. toctree::
   :maxdepth: 2
   :caption: Using the Backend



Features
--------

- HTML5 based HMI
- Supports the following industrial Protocols
	* Modbus TCP/IP
	* Modbus RTU (in development)
	* Modbus ASCII (in development)
	* BACNet/IP (in development)
	* Meter-Bus, MBus (in development)
- very low Hardware requirements for the Server


Dependencies
------------

- core/HMI
	* python 2.7
	* django>=1.6
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

The project is licensed under the GNU LESSER GENERAL PUBLIC LICENSE.
