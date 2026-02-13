"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.apps import apps
from pyscada.models import Variable, Device, Unit, DataSource
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


class VariableTest(TestCase):
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


    def test_variable_read_1(self):
        result = Variable.objects.query_datapoints(variable_ids=[self.v.pk])
        self.assertDictEqual(
            result, {"timestamp": 0, "date_saved_max": 0}
        )

    def test_variable_read_2(self):
        result = self.v.last_datapoint()
        self.assertIsNone(result)

    def test_variable_read_3(self):
        result = self.v.query_datapoints()
        self.assertTupleEqual(
            result, (None,None,None,)
        )

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
        Variable.objects.write_datapoints(
            items=[
                self.v,
            ],
            date_saved=datetime.fromtimestamp(5, UTC),
        )

    def test_variable_read(self):
        """Variable query datapoints test"""
        self.assertEqual(self.v.check_last_datapoint(), True)

        logger.debug("test_variable_read 1")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=True,
            time_max_excluded=True,
        )
        self.assertDictEqual(
            result, {"timestamp": 2.0, self.v.id: [[2.0, 100.0]], "date_saved_max": 5.0}
        )

        logger.debug("test_variable_read 2")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=False,
            time_max_excluded=True,
        )
        self.assertEqual(result, {"timestamp": 0, "date_saved_max": 0})

        logger.debug("test_variable_read 3")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=True,
            time_max_excluded=False,
        )
        self.assertDictEqual(
            result,
            {
                "timestamp": 3.0,
                self.v.id: [[2.0, 100.0], [3.0, 1000.0]],
                "date_saved_max": 5.0,
            },
        )

        logger.debug("test_variable_read 4")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=False,
            time_max_excluded=False,
        )
        self.assertDictEqual(
            result,
            {"timestamp": 3.0, self.v.id: [[3.0, 1000.0]], "date_saved_max": 5.0},
        )

        logger.debug("test_variable_read 5")
        result = self.v.query_datapoints(
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=False,
            time_max_excluded=False,
        )
        self.assertEqual(
            result,
            ([[3.0, 1000.0]], 3.0, 5.0)
        )
    def test_variable_last_datapoint(self):
        logger.debug("test_variable_last_datapoint 1")
        result = self.v.last_datapoint()
        self.assertEqual(
            result,
            ([3.0, 1000.0])
        )


class WriteRawVariableTest(TestCase):
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

    def test_variable_method_write_1(self):
        logger.debug("test_variable_method_write 1")
        self.v.write_raw_datapoints([[0, 1], [1, 10], [2, 100], [3, 1000]], date_saved=datetime.fromtimestamp(5, UTC))
        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([[0.0, 1.0], [1.0, 10.0], [2.0, 100.0], [3.0, 1000.0]], 3.0, 5.0)
        )


    def test_variable_method_write_2(self):
        logger.debug("test_variable_method_write 2")
        self.v.write_raw_datapoints([
            [0, 1, datetime.fromtimestamp(5, UTC)],
            [1, 10, datetime.fromtimestamp(6, UTC)],
            [2, 100, datetime.fromtimestamp(7, UTC)],
            [3, 1000, datetime.fromtimestamp(8, UTC)]
        ])

        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([[0.0, 1.0], [1.0, 10.0], [2.0, 100.0], [3.0, 1000.0]], 3.0, 8.0)
        )

    def test_variable_method_write_3(self):
        logger.debug("test_variable_method_write 3")
        self.v.write_raw_datapoints(
            [[0, 1, None], [1, 10, None], [2, 100, None], [3, 1000, None]],
            date_saved=datetime.fromtimestamp(8, UTC)
        )

        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([[0.0, 1.0], [1.0, 10.0], [2.0, 100.0], [3.0, 1000.0]], 3.0, 8.0)
        )

    def test_variable_method_write_4(self):
        logger.debug("test_variable_method_write 4")
        self.v.write_raw_datapoints([[0, 1, 5], [1, 10, 6], [2, 100, 7], [3, 1000, 8]])

        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([[0.0, 1.0], [1.0, 10.0], [2.0, 100.0], [3.0, 1000.0]], 3.0, 8.0)
        )

    def test_variable_manager_write(self):
        Variable.objects.write_raw_datapoints(
            datapoints={
                self.v.pk: [[4, 2], [5, 20], [6,200], [7, 2000]]
                },
            date_saved=datetime.fromtimestamp(5, UTC),
        )
        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([[4.0, 2.0], [5.0, 20.0], [6.0, 200.0], [7.0, 2000.0]], 7.0, 5.0)
        )

class VariableCacheTest(TestCase):
    def setUp(self):
        apps.get_app_config("pyscada").pyscada_app_init()

        d, created = Device.objects.get_or_create(
            short_name="dev", description="dev", protocol_id=1
        )
        unit, created = Unit.objects.get_or_create(
            unit="unit", description="unit", udunit="unit"
        )
        dts = DataSource.objects.filter(datasource_model__inline_model_name="DjangoCache").last()
        self.v, created = Variable.objects.get_or_create(
            name="var", description="var", device=d, unit=unit, datasource=dts
        )

    def test_variable_read_1(self):
        result = Variable.objects.query_datapoints(variable_ids=[self.v.pk])
        self.assertDictEqual(
            result, {"timestamp": 0, "date_saved_max": 0}
        )

    def test_variable_read_2(self):
        result = self.v.last_datapoint()
        self.assertIsNone(result)

    def test_variable_read_3(self):
        result = self.v.query_datapoints()
        self.assertTupleEqual(
            result, (None,None,None,)
        )

class WriteCacheVariableTest(TestCase):
    def setUp(self):
        apps.get_app_config("pyscada").pyscada_app_init()

        d, created = Device.objects.get_or_create(
            short_name="dev", description="dev", protocol_id=1
        )
        unit, created = Unit.objects.get_or_create(
            unit="unit", description="unit", udunit="unit"
        )
        dts = DataSource.objects.filter(datasource_model__inline_model_name="DjangoCache").last()
        self.v, created = Variable.objects.get_or_create(
            name="var", description="var", device=d, unit=unit, datasource=dts
        )
        self.time = round(datetime.now().timestamp(), 0)
        from django.core.cache import cache
        cache.clear()

    def test_variable_method_write_1(self):
        logger.debug("test_variable_method_write 1")

        #self.v.write_raw_datapoints([[0, 1], [1, 10], [2, 100], [3, 1000]], date_saved=datetime.fromtimestamp(5, UTC))
        self.v.write_raw_datapoints([
            [self.time-5, 1],
            [self.time-4, 10],
            [self.time-3, 100],
            [self.time-2, 1000]],
            date_saved=datetime.fromtimestamp(self.time-0.5, UTC)
            )
        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([
            [self.time-5, 1],
            [self.time-4, 10],
            [self.time-3, 100],
            [self.time-2, 1000]], self.time-2, self.time-0.5)
        )


    def test_variable_method_write_2(self):
        logger.debug("test_variable_method_write 2")
        self.v.write_raw_datapoints([
            [self.time-5, 1, datetime.fromtimestamp(5, UTC)],
            [self.time-4, 10, datetime.fromtimestamp(6, UTC)],
            [self.time-3, 100, datetime.fromtimestamp(7, UTC)],
            [self.time-2, 1000, datetime.fromtimestamp(8, UTC)]
        ])

        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([
            [self.time-5, 1],
            [self.time-4, 10],
            [self.time-3, 100],
            [self.time-2, 1000]], self.time-2, 8.0)
        )

    def test_variable_method_write_3(self):
        logger.debug("test_variable_method_write 3")
        self.v.write_raw_datapoints([
            [self.time-5, 1, None],
            [self.time-4, 10, None],
            [self.time-3, 100, None],
            [self.time-2, 1000, None]],
            date_saved=datetime.fromtimestamp(self.time-8, UTC)
        )

        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([
            [self.time-5, 1],
            [self.time-4, 10],
            [self.time-3, 100],
            [self.time-2, 1000]], self.time-2, self.time-8.0)
        )

    def test_variable_method_write_4(self):
        logger.debug("test_variable_method_write 4")
        self.v.write_raw_datapoints([
            [self.time-5, 1, self.time+5],
            [self.time-4, 10, self.time+6],
            [self.time-3, 100, self.time+7],
            [self.time-2, 1000, self.time+8]])

        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([
            [self.time-5, 1],
            [self.time-4, 10],
            [self.time-3, 100],
            [self.time-2, 1000]], self.time-2, self.time+8.0))

    def test_variable_manager_write(self):
        Variable.objects.write_raw_datapoints(
            datapoints={
                self.v.pk: [
                    [self.time-8, 2],
                    [self.time-9, 20],
                    [self.time-10,200],
                    [self.time-11, 2000]]
                },
            date_saved=datetime.fromtimestamp(5, UTC),
        )
        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([[self.time-8, 2.0], [self.time-9, 20.0], [self.time-10, 200.0], [self.time-11, 2000.0]], self.time-8, 5.0)
        )

class ReadVariableCacheTest(TestCase):
    def setUp(self):
        apps.get_app_config("pyscada").pyscada_app_init()

        d, created = Device.objects.get_or_create(
            short_name="dev", description="dev", protocol_id=1
        )
        unit, created = Unit.objects.get_or_create(
            unit="unit", description="unit", udunit="unit"
        )
        dts = DataSource.objects.filter(datasource_model__inline_model_name="DjangoCache").last()
        self.v, created = Variable.objects.get_or_create(
            name="var", description="var", device=d, unit=unit, datasource=dts
        )

        self.time = round(datetime.now().timestamp(), 0)
        from django.core.cache import cache
        cache.clear()

        self.v.update_values([1, 10, 100, 1000], [self.time-5, self.time-4, self.time-3, self.time-2])
        Variable.objects.write_datapoints(
            items=[
                self.v,
            ],
            date_saved=datetime.fromtimestamp(self.time-1, UTC),
        )

    def test_variable_read_1(self):
        """Variable query datapoints test"""
        self.assertEqual(self.v.check_last_datapoint(), True)

        logger.debug("test_variable_read 1")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=True,
            time_max_excluded=True,
        )
        self.assertDictEqual(
            result, {"timestamp": self.time-3, self.v.id: [[self.time-3, 100.0]], "date_saved_max": self.time-1}
        )

    def test_variable_read_2(self):
        logger.debug("test_variable_read 2")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=False,
            time_max_excluded=True,
        )
        self.assertEqual(result, {"timestamp": 0, "date_saved_max": 0})

    def test_variable_read_3(self):
        logger.debug("test_variable_read 3")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=True,
            time_max_excluded=False,
        )
        self.assertDictEqual(
            result,
            {
                "timestamp": self.time-2,
                self.v.id: [[self.time-3, 100.0], [self.time-2, 1000.0]],
                "date_saved_max": self.time-1,
            },
        )

    def test_variable_read_4(self):
        logger.debug("test_variable_read 4")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=False,
            time_max_excluded=False,
        )
        self.assertDictEqual(
            result,
            {"timestamp": self.time-2, self.v.id: [[self.time-2, 1000.0]], "date_saved_max": self.time-1},
        )

    def test_variable_read_5(self):
        logger.debug("test_variable_read 5")
        result = self.v.query_datapoints(
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=False,
            time_max_excluded=False,
        )
        self.assertEqual(
            result,
            ([[self.time-2, 1000.0]], self.time-2, self.time-1)
        )

    def test_variable_last_datapoint(self):
        logger.debug("test_variable_last_datapoint 1")
        result = self.v.last_datapoint()
        self.assertEqual(
            result,
            ([self.time-2, 1000.0])
        )

class WriteSingleValueVariableTest(TestCase):
    def setUp(self):
        apps.get_app_config("pyscada").pyscada_app_init()

        d, created = Device.objects.get_or_create(
            short_name="dev", description="dev", protocol_id=1
        )
        unit, created = Unit.objects.get_or_create(
            unit="unit", description="unit", udunit="unit"
        )
        dts = DataSource.objects.filter(datasource_model__inline_model_name="DjangoSingleValue").last()
        self.v, created = Variable.objects.get_or_create(
            name="var", description="var", device=d, unit=unit, datasource=dts
        )
        self.time = round(datetime.now().timestamp(), 0)
        from django.core.cache import cache
        cache.clear()

    def test_variable_method_write_1(self):
        logger.debug("test_variable_method_write 1")

        #self.v.write_raw_datapoints([[0, 1], [1, 10], [2, 100], [3, 1000]], date_saved=datetime.fromtimestamp(5, UTC))
        self.v.write_raw_datapoints([
            [self.time-5, 1],
            [self.time-4, 10],
            [self.time-3, 100],
            [self.time-2, 1000]],
            date_saved=datetime.fromtimestamp(self.time-0.5, UTC)
            )
        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([
            [self.time-2, 1000]], self.time-2, self.time-0.5)
        )


    def test_variable_method_write_2(self):
        logger.debug("test_variable_method_write 2")
        self.v.write_raw_datapoints([
            [self.time-5, 1, datetime.fromtimestamp(5, UTC)],
            [self.time-4, 10, datetime.fromtimestamp(6, UTC)],
            [self.time-3, 100, datetime.fromtimestamp(7, UTC)],
            [self.time-2, 1000, datetime.fromtimestamp(8, UTC)]
        ])

        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([
            [self.time-2, 1000]], self.time-2, 8.0)
        )

    def test_variable_method_write_3(self):
        logger.debug("test_variable_method_write 3")
        self.v.write_raw_datapoints([
            [self.time-5, 1, None],
            [self.time-4, 10, None],
            [self.time-3, 100, None],
            [self.time-2, 1000, None]],
            date_saved=datetime.fromtimestamp(self.time-8, UTC)
        )

        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([
            [self.time-2, 1000]], self.time-2, self.time-8.0)
        )

    def test_variable_method_write_4(self):
        logger.debug("test_variable_method_write 4")
        self.v.write_raw_datapoints([
            [self.time-5, 1, self.time+5],
            [self.time-4, 10, self.time+6],
            [self.time-3, 100, self.time+7],
            [self.time-2, 1000, self.time+8]])

        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([
            [self.time-2, 1000]], self.time-2, self.time+8.0))

    def test_variable_manager_write(self):
        Variable.objects.write_raw_datapoints(
            datapoints={
                self.v.pk: [
                    [self.time-8, 2],
                    [self.time-9, 20],
                    [self.time-10,200],
                    [self.time-11, 2000]]
                },
            date_saved=datetime.fromtimestamp(5, UTC),
        )
        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([[self.time-8, 2.0],], self.time-8, 5.0)
        )
    def test_write_multiple(self):
        self.v.update_values([1, 10 ], [self.time-10, self.time-9])
        Variable.objects.write_datapoints(
            items=[
                self.v,
            ],
            date_saved=datetime.fromtimestamp(self.time-1, UTC),
        )
        # second write
        self.v.date_saved = datetime.fromtimestamp(self.time-2, UTC)
        self.v.update_values([100, 2000], [self.time-8, self.time-7])
        self.v.write_datapoints()
        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([[self.time-7, 2000],], self.time-7, self.time-2)
        )
        # 3td write
        self.v.date_saved = datetime.fromtimestamp(self.time-1, UTC)
        self.v.update_values([30000, 400000], [self.time-6, self.time-5])
        self.v.write_datapoints()
        # 4th write
        self.v.date_saved = datetime.fromtimestamp(self.time-1, UTC)
        self.v.update_values([50000, 600000], [self.time-7, self.time-8])
        self.v.write_datapoints()
        result = self.v.query_datapoints()
        self.assertEqual(
            result, ([[self.time-5, 400000.0],], self.time-5, self.time-1)
        )


class VariableSingleValueTest(TestCase):
    def setUp(self):
        apps.get_app_config("pyscada").pyscada_app_init()

        d, created = Device.objects.get_or_create(
            short_name="dev", description="dev", protocol_id=1
        )
        unit, created = Unit.objects.get_or_create(
            unit="unit", description="unit", udunit="unit"
        )
        dts = DataSource.objects.filter(datasource_model__inline_model_name="DjangoSingleValue").last()
        self.v, created = Variable.objects.get_or_create(
            name="var", description="var", device=d, unit=unit, datasource=dts
        )

    def test_variable_read_1(self):
        result = Variable.objects.query_datapoints(variable_ids=[self.v.pk])
        self.assertDictEqual(
            result, {"timestamp": 0, "date_saved_max": 0}
        )

    def test_variable_read_2(self):
        result = self.v.last_datapoint()
        self.assertIsNone(result)

    def test_variable_read_3(self):
        result = self.v.query_datapoints()
        self.assertTupleEqual(
            result, (None,None,None,)
        )

class ReadVariableSingleValueTest(TestCase):
    def setUp(self):
        apps.get_app_config("pyscada").pyscada_app_init()

        d, created = Device.objects.get_or_create(
            short_name="dev", description="dev", protocol_id=1
        )
        unit, created = Unit.objects.get_or_create(
            unit="unit", description="unit", udunit="unit"
        )
        dts = DataSource.objects.filter(datasource_model__inline_model_name="DjangoSingleValue").last()
        self.v, created = Variable.objects.get_or_create(
            name="var", description="var", device=d, unit=unit, datasource=dts
        )

        self.time = round(datetime.now().timestamp(), 0)
        from django.core.cache import cache
        cache.clear()

        self.v.update_values([1, 10, 100, 1000], [self.time-5, self.time-4, self.time-3, self.time-2])
        Variable.objects.write_datapoints(
            items=[
                self.v,
            ],
            date_saved=datetime.fromtimestamp(self.time-1, UTC),
        )

    def test_variable_read_1(self):
        """Variable query datapoints test"""
        self.assertEqual(self.v.check_last_datapoint(), True)

        logger.debug("test_variable_read 1")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=True,
            time_max_excluded=True,
        )
        self.assertDictEqual(
            result, {"timestamp": 0, "date_saved_max": 0}
        )

    def test_variable_read_2(self):
        logger.debug("test_variable_read 2")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=False,
            time_max_excluded=True,
        )
        self.assertEqual(result, {"timestamp": 0, "date_saved_max": 0})

    def test_variable_read_3(self):
        logger.debug("test_variable_read 3")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=True,
            time_max_excluded=False,
        )
        self.assertDictEqual(
            result,
            {
                "timestamp": self.time-2,
                self.v.id: [[self.time-2, 1000.0]],
                "date_saved_max": self.time-1,
            },
        )

    def test_variable_read_4(self):
        logger.debug("test_variable_read 4")
        result = Variable.objects.query_datapoints(
            variable_ids=[self.v.pk],
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=False,
            time_max_excluded=False,
        )
        self.assertDictEqual(
            result,
            {"timestamp": self.time-2, self.v.id: [[self.time-2, 1000.0]], "date_saved_max": self.time-1},
        )

    def test_variable_read_5(self):
        logger.debug("test_variable_read 5")
        result = self.v.query_datapoints(
            time_min=self.v.timestamp_old,
            time_max=self.v.timestamp_old,
            query_first_value=False,
            time_max_excluded=False,
        )
        self.assertEqual(
            result,
            ([[self.time-2, 1000.0]], self.time-2, self.time-1)
        )

    def test_variable_last_datapoint(self):
        logger.debug("test_variable_last_datapoint 1")
        result = self.v.last_datapoint()
        self.assertEqual(
            result,
            ([self.time-2, 1000.0])
        )
