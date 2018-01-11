PyScada a open source SCADA system
==================================

A Open Source SCADA System with HTML5 HMI, build using the Django framework. If you like to setup your own SCADA system head over to http://pyscada.rtfd.io.

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
	* 1-Wire 
	* BACNet/IP (in development)
	* Meter-Bus, MBus (in development)
- very low Hardware requirements for the Server


Dependencies
------------

- core/HMI
	* python 2.7
	* django==1.11
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
- 1-Wire
	* OWFS
	* PyOWNet


What is Working and Known Issues
--------------------------------


Modbus

- Modbus TCP

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
