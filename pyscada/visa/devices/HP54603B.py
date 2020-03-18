# -*- coding: utf-8 -*-
from pyscada.visa.devices import GenericDevice
from pyscada.models import VariableProperty

import time

import logging
logger = logging.getLogger(__name__)

try:
    import numpy as np
except ImportError:
    logger.error("Need to install numpy : pip install numpy")

mdo_horiz_div_quantity = 8.0

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
        self.inst.read_termination = '\n'
        return self.inst.query('*RST;*OPC?')

    def mdo_set_horizontal_scale(self, time_per_div, **kwargs):
        self.inst.query(':TIMEBASE:MODE NORM;:TIMebase:RANGe %s;*OPC?' % str(float(time_per_div) * 10.0))
        self.inst.query(':RUN;*OPC?')
        time.sleep(2*kwargs.get("period", 1)/kwargs.get("frequency", 1000))
        self.inst.query(':STOP;*OPC?')

    def mdo_horizontal_scale_in_period(self, period=1.0, frequency=1000, **kwargs):
        mdo_horiz_scale = str(round(float(period / (10.0 * float(frequency))), 15))
        self.mdo_set_horizontal_scale(mdo_horiz_scale, period=period, frequency=frequency)

    def mdo_set_vertical_scale(self, ch=1, value=1.0, **kwargs):
        self.inst.query(':CHAN%d:RANGe %s;*OPC?' % (ch, str(value * mdo_horiz_div_quantity)))
        self.inst.query(':RUN;*OPC?')
        time.sleep(2*kwargs.get("period", 1)/kwargs.get("frequency", 1000))
        self.inst.query(':STOP;*OPC?')

    def mdo_find_vertical_scale(self, ch=1, frequency=1000, range_i=None, period=4.0, **kwargs):
        vranges = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5]
        if range_i is None:
            range_i = int(np.ceil(len(vranges) / 2.0))
        self.mdo_horizontal_scale_in_period(period=period, frequency=frequency)

        failed = 0
        range_i_min = 0
        range_i_old = -1
        while range_i < len(vranges):
            if range_i == range_i_old:
                break
            range_i_old = range_i
            # logger.debug(range_i)
            self.mdo_set_vertical_scale(ch, vranges[range_i], period=period, frequency=frequency)
            data = self.mdo_query_waveform(ch=ch, frequency=frequency, refresh=True, period=period)
            if data is None:
                failed += 1
                if failed > 3:
                    logger.debug('data is None more than 3 times')
                    break
                continue
            failed = 0
            if np.max(abs(data)) > (mdo_horiz_div_quantity * 0.9 * vranges[range_i] / 2.0):
                #logger.debug("Cas > 90% ecran")
                range_i_min = range_i + 1
                range_i_min = min(len(vranges) - 1, range_i_min)
                range_i += 1
                range_i = min(len(vranges) - 1, range_i)
                continue
            if range_i == 0:
                if np.max(abs(data)) < (mdo_horiz_div_quantity * 0.9 * vranges[range_i] / 2.0):
                    #logger.debug("Cas on ne peut pas aller plus bas")
                    break
                #logger.debug("Cas 0 donc 1")
                range_i = 1
                continue
            if (mdo_horiz_div_quantity * 0.9 * vranges[range_i - 1] / 2.0) <= np.max(abs(data)) \
                    < (mdo_horiz_div_quantity * 0.9 * vranges[range_i] / 2.0):
                #logger.debug("Cas trouve")
                break
            if np.where(vranges > 2.0 * np.max(abs(data)) / mdo_horiz_div_quantity * 0.9)[0].size == 0:
                continue
            range_i = np.where(vranges > 2.0 * np.max(abs(data)) / mdo_horiz_div_quantity * 0.9)[0][0]
            #logger.debug("Cas where")

        self.inst.query(':CHAN%d:RANGe %s;*OPC?' % (ch, str(np.max(abs(data)) * 2 / 0.7)))
        self.inst.query(':RUN;*OPC?')
        time.sleep(2*period/frequency)
        self.inst.query(':STOP;*OPC?')
        #logger.debug(range_i)

        return range_i

    def mdo_query_peak_to_peak(self, ch=1, frequency=10, period=1.0, **kwargs):
        time.sleep(0.2)
        for i in range(0, 5):
            time.sleep(2*period/frequency)
            pk2pk = float(self.inst.query(':MEASure:SOURce CHAN%d;:MEASure:VPP?' % ch))
            if pk2pk < 1e+37:
                break
            else:
                logger.debug("ch%s WRONG pk2pk : %s - i : %s" % (ch, pk2pk, i))
                self.inst.query(':RUN;*OPC?')
                time.sleep(2*period/frequency+(i+1)/10)
                self.inst.query(':STOP;*OPC?')
        return pk2pk

    def mdo_gain(self, source1=1, source2=2, frequency=10, period=1.0, **kwargs):
        return 20 * np.log10(self.mdo_query_peak_to_peak(ch=source2, frequency=frequency, period=period) /
                             self.mdo_query_peak_to_peak(ch=source1, frequency=frequency, period=period))

    def mdo_set_trigger_level(self, ch=1, level=0, **kwargs):
        self.inst.query(':TRIGger:LEVel %s;*OPC?;' % str(level))

    def mdo_set_trigger_source(self, ch=1, **kwargs):
        self.inst.query(':TRIGger:SOURce CHAN%d;*OPC?;' % ch)

    def mdo_prepare(self, **kwargs):
        logger.debug("IDN : %s" % self.inst.query('*IDN?'))
        self.inst.query(':RUN;*OPC?')  # run
        self.inst.query(':ACQuire:TYPE NORM;:TRIGger:COUPling DC;:TRIGger:MODE NORM;'
                        ':CHAN1:OFFSet 0;:CHAN2:OFFSet 0;*OPC?')
        self.inst.query(':CHANnel1:COUPling AC;:CHANnel2:COUPling AC;:VIEW CHAN1;:VIEW CHAN2;*OPC?')

    def mdo_query_waveform(self, ch=1, points_resolution=100, frequency=1000, period=4.0, **kwargs):

        # io config
        points_resolution = points_resolution if points_resolution in [100, 200, 250, 400, 500, 1000, 2000] else 2000
        self.inst.write(':WAVeform:POINts %s' % points_resolution)
        self.inst.write(':WAVeform:FORMat BYTE')
        self.inst.write(':WAVeform:BYTeorder LSBF')
        self.inst.write(':WAVeform:SOURce CHAN%d' % ch)  # channel

        # data query
        self.inst.query('*OPC?')
        time.sleep(0.2)
        for i in range(0, 5):
            time.sleep(2*period/frequency)
            bin_wave = self.inst.query_binary_values(':WAVeform:DATA?', datatype='b', container=np.array,
                                                     delay=2 * 10 / frequency)
            if np.std(bin_wave) == 0:
                #logger.debug("np.std(bin_wave) == 0 : %s" % i)
                self.inst.query(':RUN;*OPC?')
                time.sleep(2*period/frequency+(i+1)/10)
                self.inst.query(':STOP;*OPC?')
                bin_wave = self.inst.query_binary_values(':WAVeform:DATA?', datatype='b', container=np.array,
                                                         delay=2 * 10 / frequency)
            else:
                break

        # retrieve scaling factors
        vscale = float(self.inst.query(':WAVeform:YINCrement?'))  # volts / level
        voff = float(self.inst.query(':WAVeform:YORigin?'))  # reference voltage
        vpos = float(self.inst.query(':WAVeform:YREFerence?'))  # reference position (level)

        unscaled_wave = np.array(bin_wave, dtype='double')  # data type conversion
        scaled_wave = [(a-vpos)*vscale if a > 0 else (a+vpos)*vscale if a < 0 else a for a in unscaled_wave]

        scaled_wave_mini = list()
        if points_resolution < int(len(scaled_wave)):
            for i in range(0, points_resolution):
                scaled_wave_mini.append(scaled_wave[i * int(len(scaled_wave) / points_resolution)])
        else:
            scaled_wave_mini = scaled_wave

        return np.asarray(scaled_wave_mini)

    def mdo_get_phase(self, frequency=1000, period=4.0, **kwargs):
        # Start reading the phase
        phase = 0
        # self.mdo_horizontal_scale_in_period(period=4.0, frequency=frequency)
        # self.inst.query(':STOP;*OPC?')

        # a = self.mdo_query_waveform(ch=1, frequency=frequency, refresh=True, points_resolution=10000)
        # b = self.mdo_query_waveform(ch=2, frequency=frequency, refresh=False, points_resolution=10000)
        # phase2 = self.find_phase_2_signals(a, b, frequency, self.mdo_horizontal_time())
        mean_phase = 0
        for i in range(0, 10):
            time.sleep((i+1)/10)
            a = self.mdo_query_waveform(ch=1, frequency=frequency, refresh=True, points_resolution=10000, period=period)
            b = self.mdo_query_waveform(ch=2, frequency=frequency, refresh=False, points_resolution=10000,
                                        period=period)
            phase1 = self.find_phase_2_signals(a, b, frequency, self.mdo_horizontal_time())
            time.sleep((i+1)/10)
            a = self.mdo_query_waveform(ch=1, frequency=frequency, refresh=True, points_resolution=10000, period=period)
            b = self.mdo_query_waveform(ch=2, frequency=frequency, refresh=False, points_resolution=10000,
                                        period=period)
            phase2 = self.find_phase_2_signals(a, b, frequency, self.mdo_horizontal_time())
            time.sleep((i+1)/10)
            a = self.mdo_query_waveform(ch=1, frequency=frequency, refresh=True, points_resolution=10000, period=period)
            b = self.mdo_query_waveform(ch=2, frequency=frequency, refresh=False, points_resolution=10000,
                                        period=period)
            phase3 = self.find_phase_2_signals(a, b, frequency, self.mdo_horizontal_time())
            stdev_phase = np.std([phase1, phase2, phase3])
            mean_phase = np.mean([phase1, phase2, phase3])
            check_phase = abs(stdev_phase/mean_phase)
            if check_phase < 0.1 or mean_phase == 0:
                break
            else:
                logger.debug('%s check_phase too big : %s (%s %s %s)' % (i, check_phase, phase1, phase2, phase3))
        self.inst.query(':RUN;*OPC?')
        # logger.debug('phase oscillo = %s - phase numpy = %s' % (phase, phase2))
        return phase, mean_phase

    def mdo_horizontal_time(self):
        horizontal_time = float(self.inst.query(':TIMebase:RANGe?'))
        return horizontal_time

    def mdo_xincr(self):
        return float(self.inst.query(':WAVeform:XINCrement?'))

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
        # logger.debug('tmax = %s - nsamples = %s' % (tmax, nsamples))  # length of time series (seconds)

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
        # recovered_phase_shift_before = -1 * 2 * np.pi * (((0.5 + dt[np.argmax(xcorr) - 1] / period) % 1.0) - 0.5)
        # recovered_phase_shift_after = -1 * 2 * np.pi * (((0.5 + dt[np.argmax(xcorr) + 1] / period) % 1.0) - 0.5)
        # logger.debug('phase - 1 = %s - phase = %s - phase + 1 = %s' %
        #             (recovered_phase_shift_before * 180 / np.pi, recovered_phase_shift * 180 / np.pi,
        #              recovered_phase_shift_after * 180 / np.pi))

        return recovered_phase_shift * 180 / np.pi
