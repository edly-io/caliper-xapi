"""
Test the CaliperEnvelopProcessor
"""
from datetime import datetime
from unittest import TestCase

from mock import patch, sentinel
from pytz import UTC

from edx_analytics_transformers.processors.caliper_envelop import CaliperEnvelopProcessor
from edx_analytics_transformers.transformers.caliper.helpers import convert_datetime_to_iso
from edx_analytics_transformers.transformers.caliper.constants import CALIPER_EVENT_CONTEXT


FROZEN_TIME = datetime(2013, 10, 3, 8, 24, 55, tzinfo=UTC)


class TestCaliperEnvelopProcessor(TestCase):
    """
    Test the Caliper Envelop processor
    """

    def setUp(self):
        super().setUp()
        self.sample_event = {
            'name': str(sentinel.name)
        }
        self.sensor_id = 'http://test.sensor.com'

    @patch('edx_analytics_transformers.processors.caliper_envelop.datetime')
    def test_caliper_envelop_processor(self, mocked_datetime):
        mocked_datetime.now.return_value = FROZEN_TIME

        result = CaliperEnvelopProcessor(sensor_id=self.sensor_id)(self.sample_event)
        self.assertEqual(result, {
            'sensor': self.sensor_id,
            'sendTime': convert_datetime_to_iso(str(FROZEN_TIME)),
            'data': self.sample_event,
            'dataVersion': CALIPER_EVENT_CONTEXT
        })
