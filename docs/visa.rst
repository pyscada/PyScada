Discover VISA devices
=====================

To discover GPIB/USB(/LXI?) devices run:

::

    sudo python3
    import pyvisa
    rm=pyvisa.ResourceManager('@py')
    rm.list_resources()  # example : ('ASRL/dev/ttyAMA0::INSTR', 'USB0::1689::1032::C023569::0::INSTR', 'USB0::1689::851::1525638::0::INSTR')
    inst=rm.open_resource('USB0::1689::851::1525638::0::INSTR'')
    inst.query('*IDN?')  # example : 'TEKTRONIX,AFG1022,1525638,SCPI:99.0 FV:V1.1.2\n'
