# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.generic.devices import GenericDevice
from pyscada.models import VariableProperty

from scipy import signal
import numpy as np
from time import time_ns

import logging

logger = logging.getLogger(__name__)


class Handler(GenericDevice):
    """
    Generic dummy device
    """

    def read_data_and_time(self, variable_instance):
        """
        Generic waveform device : use variable properties to configure the waveform.
        """
        t = time_ns() / 1000000000.0
        default = {
            "type": "sinus",  # sinus, square, triangle
            "amplitude": 1.0,  # peak to peak value
            "offset": 0.0,  # waveform offset value
            "start_timestamp": 0.0,  # in second from 01/01/1970 00:00:00
            "frequency": 0.1,  # Hz
            "duty_cycle": 0.5,  # between 0 and 1, duty cycle for square and for triangle : Width of the rising ramp as a proportion of the total cycle. Default is 1, producing a rising ramp, while 0 produces a falling ramp. width = 0.5 produces a triangle wave. If an array, causes wave shape to change over time, and must be the same length as t.
        }

        def type_default(fct):
            if str(fct) in ["sinus", "square", "triangle"]:
                return str(fct)
            else:
                return "sinus"

        def positive_float(i):
            if i >= 0:
                return i
            else:
                return 0

        def number(i):
            try:
                return float(i)
            except Exception as e:
                logger.warning(f"A waveform property is not a number, it is {i}")
                return 0

        def positive_float_strict(i):
            if i > 0:
                return i
            else:
                return 1

        def duty_cycle(i):
            if i >= 0 and i <= 1:
                return i
            else:
                return 0.5

        default_allowed = {
            "type": type_default,
            "amplitude": positive_float_strict,
            "offset": number,
            "start_timestamp": positive_float,
            "frequency": positive_float_strict,
            "duty_cycle": duty_cycle,
        }

        for prop in default:
            vp = VariableProperty.objects.filter(variable=variable_instance, name=prop)
            if vp.exists():
                default[prop] = default_allowed[prop](vp.first().value())

        if default["type"] == "sinus":
            out = (
                default["amplitude"]
                / 2.0
                * np.sin(
                    2.0
                    * np.pi
                    * (t - default["start_timestamp"])
                    * default["frequency"]
                )
                + default["offset"]
            )
        elif default["type"] == "square":
            out = (
                default["amplitude"]
                / 2.0
                * signal.square(
                    2.0
                    * np.pi
                    * (t - default["start_timestamp"])
                    * default["frequency"],
                    default["duty_cycle"],
                )
                + default["offset"]
            )
        elif default["type"] == "triangle":
            out = (
                default["amplitude"]
                / 2.0
                * signal.sawtooth(
                    2.0
                    * np.pi
                    * (t - default["start_timestamp"])
                    * default["frequency"],
                    default["duty_cycle"],
                )
                + default["offset"]
            )

        return out, t

    def write_data(self, variable_id, value, task):
        """
        Generic dummy device : return the value to write.
        """
        return value
