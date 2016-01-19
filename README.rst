PyScada a open source SCADA system
==================================

A Open Source SCADA System with HTML5 HMI, build using the Django framework. If you like to setup your own _SCADA_ system head over to the :doc:`installation` section.

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

Installation
------------

Detailed installation instruction can be found at: https://pyscada.rtfd.org .


Contribute
----------

 - Issue Tracker: https://github.com/trombastic/PyScada/issues
 - Source Code: https://github.com/trombastic/PyScada


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.
