#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyscada.models import CalculatedVariable

from time import time
import logging

logger = logging.getLogger(__name__)


def startup(self):
    """
    write your code startup code here, don't change the name of this function
    :return:
    """
    pass


def shutdown(self):
    """
    write your code shutdown code here, don't change the name of this function
    :return:
    """
    pass


def script(self):
    """
    write your code loop code here, don't change the name of this function

    :return:
    """

    cvs = CalculatedVariable.objects.all()
    for cv in cvs:
        if (
            cv.variable_calculated_fields.active
            and cv.period in cv.variable_calculated_fields.period_fields.all()
            and cv.store_variable.active
        ):
            cv.check_to_now()
