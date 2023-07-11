PyScada a open source SCADA system
==================================

A Open Source SCADA System with HTML5 HMI, build using the Django framework. If you like to setup your own SCADA system head over to http://pyscada.rtfd.io.

Features
--------

* HTML5 based HMI
* Supports the following

 * industrial Protocols

  * `Modbus <https://github.com/pyscada/PyScada-Modbus>`_ TCP/IP - RTU - ASCII - Binary (using `pyModbus <https://github.com/pymodbus-dev/pymodbus>`_)
  * `Phant <https://github.com/pyscada/PyScada-Phant>`_ (see http://phant.io/)
  * `VISA <https://github.com/pyscada/PyScada-VISA>`_ (using `pyVISA <https://pypi.python.org/pypi/PyVISA>`_)
  * `1-Wire <https://github.com/pyscada/PyScada-OneWire>`_
  * `BACNet/IP <https://github.com/pyscada/PyScada-BACNet>`_ (in development) (using `BACpypes <https://github.com/JoelBender/bacpypes>`_ and `BAC0 <https://github.com/ChristianTremblay/BAC0>`_)
  * `MeterBus (MBus) <https://github.com/pyscada/PyScada-MeterBus>`_ (in development) (using `pyMeterBus <https://github.com/ganehag/pyMeterBus/>`_)
  * `SMBus <https://github.com/pyscada/PyScada-SMBus>`_ (using `smbus2 <https://github.com/kplindegaard/smbus2>`_)
  * `GPIO <https://github.com/pyscada/PyScada-GPIO>`_ (using `RPi.GPIO <https://pypi.org/project/RPi.GPIO/>`_)
  * `SystemStat <https://github.com/pyscada/PyScada-SystemStat>`_
  * `OPC-UA <https://github.com/clavay/PyScada-OPCUA>`_ (using `opcua-asyncio <https://github.com/FreeOpcUa/opcua-asyncio>`_)
  * `SML (Smart Meter Language) <https://github.com/gkend/PyScada-SML>`_ (using `pySML <https://github.com/mtdcr/pysml>`_)
  * `File read/write <https://github.com/pyscada/PyScada-File>`_
  * `Serial <https://github.com/clavay/PyScada-Serial>`_
  * `WebService <https://github.com/clavay/PyScada-WebService>`_

 * devices

  * Generic dummy device
  * `PT104 <https://github.com/pyscada/PyScada-PT104>`_ (using `Pico PT-104 <https://www.picotech.com/data-logger/pt-104/high-accuracy-temperature-daq>`_)

 * scripts

  * `Scripting <https://github.com/pyscada/PyScada-Scripting>`_

 * system tools

  * `EMS <https://github.com/pyscada/PyScada-EMS>`_

 * event management, data export, mail notification

* very low Hardware requirements for the server

Structure
---------

.. image:: https://github.com/pyscada/PyScada/raw/master/docs/pic/PyScada_module_overview.png
    :width: 600px

Dependencies
------------

- core/HMI
	* python>=3.8
	* django==4.2
	* numpy>=1.6.0
	* pillow
	* python-daemon

What is Working
---------------

 - Modbus TCP/RTU/BIN
 - Visa (at least for the devices in the visa/devices folder)
 - Systemstat
 - OneWire (only DS18B20)
 - phant (no known issues)
 - smbus (at least for the devices in the smbus/devices folder)
 - gpio (at least for the raspberry pi)
 - webservice (json and xml parsing)
 - systemstat
 - scripting
 - event (no known issues)
 - export (no known issues)
 - hmi (no known issues)

What is not Working/Missing
---------------------------

 - Documentation
 - SysV init daemon handling
 - BACNet (due to the lack of hardware to test)
 - OPC-UA (need more tests)
 - MeterBus (need more tests)


Installation
------------

Detailed installation instruction can be found at: http://pyscada.rtfd.io .


Contribute
----------

 - Issue Tracker: https://github.com/pyscada/PyScada/issues
 - Source Code: https://github.com/pyscada/PyScada


License
-------

The project is licensed under the _GNU Affero General Public License v3 (AGPLv3).
