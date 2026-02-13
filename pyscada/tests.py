"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.apps import apps
from pyscada.models import Variable, Device, Unit
from datetime import datetime
from pytz import UTC

import logging

logger = logging.getLogger(__name__)


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class ReadVariableTest(TestCase):
    def setUp(self):
        apps.get_app_config("pyscada").pyscada_app_init()

        d, created = Device.objects.get_or_create(
            short_name="dev", description="dev", protocol_id=1
        )
        unit, created = Unit.objects.get_or_create(
            unit="unit", description="unit", udunit="unit"
        )
        self.v, created = Variable.objects.get_or_create(
            name="var", description="var", device=d, unit=unit
        )
        self.v.update_values([1, 10, 100, 1000], [0, 1, 2, 3])
        Variable.objects.write_multiple(
            items=[
                self.v,
            ],
            date_saved=datetime.fromtimestamp(5, UTC),
        )

    def test_variable_read(self):
        """Variable read multiple test"""
        self.assertEqual(self.v.query_prev_value(), True)

        logger.debug("test_variable_read 1")
        result = Variable.objects.read_multiple(
            variable=self.v,
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            time_in_ms=False,
            query_first_value=True,
            time_max_excluded=True,
        )
        self.assertEqual(
            result, {"timestamp": 2.0, self.v.id: [[2.0, 100.0]], "date_saved_max": 5.0}
        )

        logger.debug("test_variable_read 2")
        result = Variable.objects.read_multiple(
            variable=self.v,
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            time_in_ms=False,
            query_first_value=False,
            time_max_excluded=True,
        )
        self.assertEqual(result, {"timestamp": 0, "date_saved_max": 0})

        logger.debug("test_variable_read 3")
        result = Variable.objects.read_multiple(
            variable=self.v,
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            time_in_ms=False,
            query_first_value=True,
            time_max_excluded=False,
        )
        self.assertEqual(
            result,
            {
                "timestamp": 3.0,
                self.v.id: [[2.0, 100.0], [3.0, 1000.0]],
                "date_saved_max": 5.0,
            },
        )

        logger.debug("test_variable_read 4")
        result = Variable.objects.read_multiple(
            variable=self.v,
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            time_in_ms=False,
            query_first_value=False,
            time_max_excluded=False,
        )
        self.assertEqual(
            result,
            {"timestamp": 3.0, self.v.id: [[3.0, 1000.0]], "date_saved_max": 5.0},
        )
