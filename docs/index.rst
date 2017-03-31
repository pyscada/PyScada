PyScada a open source SCADA system
==================================

A Open Source SCADA System with HTML5 HMI, build using the Django framework. If you like to setup your own _SCADA_ system head over to the :doc:`installation` section.


.. toctree::
   :maxdepth: 2
   :caption: Installation and Commandline 

   installation
   django_settings
   nginx_setup
   update
   command-line
   frontend
   backend





Features
--------

- HTML5 based HMI
- Supports the following industrial Protocols
	* Modbus TCP/IP
	* Modbus RTU
	* Modbus ASCII
	* Modbus Binary
	* Phant http://phant.io/
	* VISA https://pypi.python.org/pypi/PyVISA
	* 1-Wire (only RaspberryPi)
	* BACNet/IP (in development)
	* Meter-Bus, MBus (in development)
- very low Hardware requirements for the Server


Dependencies
------------

- core/HMI
	* python 2.7
	* django==1.10
	* numpy>=1.6.0
	* pillow
	* python-daemon
- ModbusMaster
	* pymodbus>=1.2
- HDF5Export
	* h5py>=2.1.1
- SystemStatistics
	* psutil
- VISA
    * PyVisa >= 1.8
- BACNet/IP
	* bacpypes


Contribute
----------

 - Issue Tracker: https://github.com/trombastic/PyScada/issues
 - Source Code: https://github.com/trombastic/PyScada


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.
