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

Structure
---------

.. image:: https://github.com/trombastic/PyScada/raw/dev/0.7.x/docs/pic/PyScada_module_overview.png
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

@cwraig wrote some nice Blog articles on different topics for using PyScada with the Raspberry Pi:
 - `PyScada on Raspberry PI for temperature monitoring with DS18B20 on 1-Wire – Part 1 – Software Installation <https://cwraig.id.au/2017/09/17/pyscada-on-raspberry-pi-for-temperature-monitoring-with-ds18b20-on-1-wire-part-1-software- installation/>`_
 - `PyScada on Raspberry PI for temperature monitoring with DS18B20 on 1-Wire – Part 2 – DS18B20 Hardware and Software <https://cwraig.id.au/2017/09/17/pyscada-on-raspberry-pi-for-temperature-monitoring-with-ds18b20-on-1-wire-part-2-ds18b20-hardware-and-software/>`_
 - `PyScada on Raspberry PI for temperature monitoring with DS18B20 on 1-Wire – Part 3 – PyScada Basic Configuration <https://cwraig.id.au/2017/09/21/pyscada-on-raspberry-pi-for-temperature-monitoring-with-ds18b20-on-1-wire-part-3-pyscada-basic-configuration/>`_
 - `PyScada on Raspberry PI for temperature monitoring with DS18B20 on 1-Wire – Part 4 – PyScada HMI Configuration <https://cwraig.id.au/2017/09/24/pyscada-on-raspberry-pi-for-temperature-monitoring-with-ds18b20-on-1-wire-part-4-pyscada-hmi-configuration/>`_
 - `PyScada on Raspberry PI for Modbus RTU <https://cwraig.id.au/2018/01/21/pyscada-on-raspberry-pi-for-modbus-rtu/>`_


Contribute
----------

 - Issue Tracker: https://github.com/trombastic/PyScada/issues
 - Source Code: https://github.com/trombastic/PyScada


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.
-