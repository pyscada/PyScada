PyScada a open source SCADA system
==================================

A Open Source SCADA System with HTML5 HMI, build using the Django framework. If you like to setup your own SCADA system head over to the http://pyscada.readthedocs.io/en/dev-0.7.x/installation.html section.

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
	* 1-Wire (only experimental only RPi3)
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

Installation
------------

Detailed installation instruction can be found at: http://pyscada.rtfd.io .


Contribute
----------

 - Issue Tracker: https://github.com/trombastic/PyScada/issues
 - Source Code: https://github.com/trombastic/PyScada


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.
