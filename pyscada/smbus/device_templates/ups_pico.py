# -*- coding: utf-8 -*-


def ups_pico(smbus_device,info):
    """
    query data via smbus (I2C) from a UPS Pico  device
    """
    if info == 'ad1':
        data = smbus_device.read_word_data(0x69, 0x05)
        data = format(data,"02x")
        return (float(data) / 100) # °C
    
    if info == 'ad2':
        data = smbus_device.read_word_data(0x69, 0x07)
        data = format(data,"02x")
        return (float(data) / 100) # °C
    
    if info == 'rpi_level':
        data = smbus_device.read_word_data(0x69, 0x03)
        data = format(data,"02x")
        return (float(data) / 100) # Volt
    
    if info == 'bat_level':
        data = smbus_device.read_word_data(0x69, 0x01)
        data = format(data,"02x")
        return (float(data) / 100) # Volt
    
    if info == 'pwr_mode':
        data = smbus_device.read_word_data(0x69, 0x00)
        return data & ~(1 << 7) # 1 RPi, 2 Bat
    
    if info == 'sot23_temp':
        data = smbus_device.read_byte_data(0x69, 0x0C)
        data = format(data,"02x")
        return data

    if info == 'to92_temp':
        data = smbus_device.read_byte_data(0x69, 0x0D)
        data = format(data,"02x")
        return data

    return None