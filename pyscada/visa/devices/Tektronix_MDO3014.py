# -*- coding: utf-8 -*-
from pyscada.visa.devices import GenericDevice
from pyscada.models import VariableProperty

import time

import logging
logger = logging.getLogger(__name__)

try:
    import numpy as np
except:
    logger.error("Need to install numpy : pip install numpy")


class Handler(GenericDevice):
    """
    Tektronix MDO3014 and other Devices with the same command set
    """

    def read_data(self, device_property):
        """
        read values from the device
        """
        if self.inst is None:
            logger.error("Visa-MDO3014-read data-Self.inst : None")
            return None
        if device_property == 'present_value':
            return self.parse_value(self.inst.query(':READ?'))
        else:
            value = self.inst.query(device_property)
            logger.info("Visa-MDO3014-read data-property : %s - value : %s" % (device_property, value))
            return self.parse_value(value)
        return None

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        variable = self._variables[variable_id]
        if task.property_name != '':
            # write the freq property to VariableProperty use that for later read
            VariableProperty.objects.update_or_create_property(variable=variable, name=task.property_name.upper(),
                                                               value=value, value_class='FLOAT64')
            return True
        if variable.visavariable.variable_type == 0:  # configuration
            # only write to configuration variables
            pass
        else:
            return False

    def parse_value(self, value):
        """
        takes a string in the Tektronix MDO3014 format and returns a float value or None if not parseable
        """
        try:
            return float(value)
        except:
            return None

    # MDO functions
    def reset_instrument(self):
        return self.inst.query('*RST;*OPC?')

    def mdo_horizontal_scale_in_period(self, period=1.0, frequency=1000):
        mdo_horiz_scale = str(round(float(period / (10.0 * float(frequency))), 6))
        self.inst.query(':HORIZONTAL:SCALE %s;*OPC?' % mdo_horiz_scale)

    def mdo_find_vertical_scale(self, ch=1, frequency=1000, range_i=None):
        vranges = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]
        if range_i is None:
            range_i = int(np.ceil(len(vranges) / 2.0))
        self.mdo_horizontal_scale_in_period(period=1.0, frequency=frequency)

        failed = 0
        mdo_div_quantity = 8.0
        range_i_min = 0
        while range_i < len(vranges):
            logger.debug(range_i)
            self.inst.query(':CH%d:SCALE %s;*OPC?' % (ch, str(vranges[range_i])))
            data = self.mdo_query_waveform(ch=ch, frequency=frequency, refresh=True)
            if data is None:
                failed += 1
                if failed > 3:
                    logger.debug('data is None more than 3 times')
                    break
                continue
            failed = 0
            if np.max(abs(data)) > (mdo_div_quantity * 0.9 * vranges[range_i] / 2.0):
                range_i_min = range_i + 1
                range_i += 3
                range_i = min(len(vranges) - 1, range_i)
            if range_i == 0:
                if np.max(abs(data)) < (mdo_div_quantity * 0.9 * vranges[range_i] / 2.0):
                    break
                range_i = 1
                continue
            if (mdo_div_quantity * 0.9 * vranges[range_i - 1] / 2.0) <= np.max(abs(data)) \
                    < (mdo_div_quantity * 0.9 * vranges[range_i] / 2.0):
                break
            range_i = max(range_i_min, np.where(vranges > 2.0 * np.max(abs(data)) / mdo_div_quantity * 0.9)[0][0])

        logger.debug(range_i)
        mdo_ch2_scale = str(vranges[range_i])
        logger.debug("Freq = %s - horiz scale = %s - ch2 scale = %s"
                     % (int(frequency), str(round(float(1.0 / (10.0 * float(frequency))), 6)), mdo_ch2_scale))
        return range_i

    def mdo_query_peak_to_peak(self, ch=1):
        return float(self.inst.query((':MEASUrement:IMMed:SOUrce1 CH%d;:MEASUREMENT:IMMED:TYPE PK2PK;'
                                      ':MEASUREMENT:IMMED:VALUE?' % ch)))

    def mdo_gain(self, source1=1, source2=2):
        return 20 * np.log10(self.mdo_query_peak_to_peak(ch=source2) / self.mdo_query_peak_to_peak(ch=source1))

    def mdo_prepare_for_bode(self, vpp):
        self.inst.query(':SEL:CH1 1;:SEL:CH2 1;:HORIZONTAL:POSITION 0;:CH1:YUN "V";:CH1:SCALE %s;:CH2:YUN "V";'
                        ':CH2:BANdwidth 10000000;:CH1:BANdwidth 10000000;:TRIG:A:TYP EDGE;:TRIG:A:EDGE:COUPLING AC;'
                        ':TRIG:A:EDGE:SOU CH1;:TRIG:A:EDGE:SLO FALL;:TRIG:A:MODE NORM;:CH1:COUP AC;:CH2:COUP AC;'
                        ':TRIG:A:LEV:CH1 0;*OPC?;' % str(1.2 * float(vpp) / (2 * 4)))

    def mdo_query_waveform(self, ch=1, points_resolution=100, frequency=1000, refresh=False):
        self.inst.query(':SEL:CH%d 1;:HORIZONTAL:POSITION 0;:CH%d:YUN "V";'
                        ':CH%d:BANdwidth 10000000;:TRIG:A:TYP EDGE;:TRIG:A:EDGE:COUPLING AC;:TRIG:A:EDGE:SOU CH%d;'
                        ':TRIG:A:EDGE:SLO FALL;:TRIG:A:MODE NORM;*OPC?' % (ch, ch, ch, ch))

        # io config
        self.inst.write('header 0')
        self.inst.write('data:encdg SRIBINARY')
        self.inst.write('data:source CH%d' % ch)  # channel
        self.inst.write('data:snap')  # last sample
        self.inst.write('wfmoutpre:byt_n 1')  # 1 byte per sample

        if refresh:
            # acq config
            self.inst.write('acquire:state 0')  # stop
            self.inst.write('acquire:stopafter SEQUENCE')  # single
            self.inst.write('acquire:state 1')  # run

        # data query
        self.inst.query('*OPC?')
        bin_wave = self.inst.query_binary_values('curve?', datatype='b', container=np.array, delay=2 * 10 / frequency)

        # retrieve scaling factors
        # tscale = float(self.inst_mdo.query('wfmoutpre:xincr?'))
        vscale = float(self.inst.query('wfmoutpre:ymult?'))  # volts / level
        voff = float(self.inst.query('wfmoutpre:yzero?'))  # reference voltage
        vpos = float(self.inst.query('wfmoutpre:yoff?'))  # reference position (level)

        # create scaled vectors
        # horizontal (time)
        # total_time = tscale * record
        # tstop = tstart + total_time
        # scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double')  # data type conversion
        scaled_wave = (unscaled_wave - vpos) * vscale + voff
        scaled_wave = scaled_wave.tolist()

        scaled_wave_mini = list()
        for i in range(0, points_resolution):
            scaled_wave_mini.append(scaled_wave[i * int(len(scaled_wave) / points_resolution)])

        return np.asarray(scaled_wave_mini)

    def mdo_get_phase(self, source1=1, source2=2, frequency=1000):
        self.mdo_horizontal_scale_in_period(period=4.0, frequency=frequency)
        self.inst.write(':MEASUrement:IMMed:SOUrce1 CH%d;:MEASUrement:IMMed:SOUrce2 CH%d;'
                        ':MEASUREMENT:IMMed:TYPE PHASE' % (source1, source2))

        # Start reading the phase
        retries = 0
        while retries < 3:
            self.inst.write('acquire:state 0')  # stop
            self.inst.write('acquire:stopafter SEQUENCE')  # single
            self.inst.write('acquire:state 1')  # run
            self.inst.query('*OPC?')
            phase = float(self.inst.query(':MEASUREMENT:IMMED:VALUE?;'))
            retries += 1
            if -360 < phase < 360:
                break
            if retries >= 3:
                phase = None
                break
            logger.debug('Wrong phase = %s' % phase)
            time.sleep(1)
        if phase < -180 and phase is not None:
            phase += 360
        self.mdo_horizontal_scale_in_period(period=4.0, frequency=frequency)

        a = self.mdo_query_waveform(ch=1, frequency=frequency, refresh=True, points_resolution=10000)
        b = self.mdo_query_waveform(ch=2, frequency=frequency, refresh=False, points_resolution=10000)
        phase2 = self.find_phase_2_signals(a, b, frequency, self.mdo_horizontal_time())
        logger.debug('phase oscillo = %s - phase scipy = %s' % (phase, phase2))
        return phase, phase2

    def mdo_horizontal_time(self):
        record = int(self.inst.query('horizontal:recordlength?'))
        tscale = float(self.inst.query('wfmoutpre:xincr?'))
        return tscale * record

    def fft(self, eta):
        nfft = len(eta)
        hanning = np.hanning(nfft) * eta
        spectrum_hanning = abs(np.fft.fft(hanning))
        spectrum_hanning = spectrum_hanning * 2 * 2 / nfft  # also correct for Hann filter
        return spectrum_hanning

    def find_phase_2_signals(self, a, b, frequency, tmax):
        period = 1 / frequency  # period of oscillations (seconds)
        tmax = float(tmax)
        nsamples = int(a.size)
        logger.debug('tmax = %s - nsamples = %s' % (tmax, nsamples))  # length of time series (seconds)

        # construct time array
        t = np.linspace(0.0, tmax, nsamples, endpoint=False)

        # calculate cross correlation of the two signals
        xcorr = np.correlate(a, b, "full")

        # The peak of the cross-correlation gives the shift between the two signals
        # The xcorr array goes from -nsamples to nsamples
        dt = np.linspace(-t[-1], t[-1], 2 * nsamples - 1)
        recovered_time_shift = dt[np.argmax(xcorr)]

        # force the phase shift to be in [-pi:pi]
        recovered_phase_shift = -1 * 2 * np.pi * (((0.5 + recovered_time_shift / period) % 1.0) - 0.5)
        recovered_phase_shift_before = -1 * 2 * np.pi * (((0.5 + dt[np.argmax(xcorr) - 1] / period) % 1.0) - 0.5)
        recovered_phase_shift_after = -1 * 2 * np.pi * (((0.5 + dt[np.argmax(xcorr) + 1] / period) % 1.0) - 0.5)
        logger.debug('phase - 1 = %s - phase = %s - phase + 1 = %s' %
                     (recovered_phase_shift_before * 180 / np.pi, recovered_phase_shift * 180 / np.pi,
                      recovered_phase_shift_after * 180 / np.pi))

        return recovered_phase_shift * 180 / np.pi
