PyScada a open source SCADA system
==================================

A Open Source SCADA System with HTML5 HMI, build using the Django framework. If you like to setup your own SCADA system head over to http://pyscada.rtfd.io.

Planed Changes and ToDos for Version 0.8.0
------------------------------------------

This section describes the planed changes for the next major upgrade to PyScada and will be removed after the upgrade.

- upgrade to Django 4.2 LTS
        * deal with the app_label not defined error for pyscada/models.py
- moving the plugins in separate repositories
        * pyscada.modbus
        * pyscada.visa
        * pyscada.phant
        * pyscada.onewire
        * pyscada.systemstat
- renaming name of the default branche to "main"

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

Structure
---------

.. image:: https://github.com/pyscada/PyScada/raw/master/docs/pic/PyScada_module_overview.png
    :width: 600px

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


What is Working
---------------

 - Modbus TCP/RTU/BIN
 - Visa (at least for the Devices in the visa/devices folder)
 - Systemstat
 - OneWire (only DS18B20)
 - phant (no known issues)
 - smbus (at least for the Devices in the smbus/device_templates folder)
 - event (no known issues)
 - export (no known issues)
 - hmi (no known issues)

What is not Working/Missing
---------------------------

 - Documentation
 - SysV init daemon handling
 - BACNet (due to the lack of hardware to test)


Installation
------------

Detailed installation instruction can be found at: http://pyscada.rtfd.io .


Contribute
----------

 - Issue Tracker: https://github.com/pyscada/PyScada/issues
 - Source Code: https://github.com/pyscada/PyScada


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.
-