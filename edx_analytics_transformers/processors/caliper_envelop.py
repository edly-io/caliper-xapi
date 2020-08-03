"""
Envelope the caliper transformed event.
"""
from datetime import datetime

from pytz import UTC

from edx_analytics_transformers.transformers.caliper.constants import CALIPER_EVENT_CONTEXT
from edx_analytics_transformers.transformers.caliper.helpers import convert_datetime_to_iso


class CaliperEnvelopProcessor:
    """
    Envelope the caliper transformed event.
    """
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id

    def __call__(self, event):
        """
        Envelope the caliper transformed event.

        Arguments:
            event (dict):   IMS Caliper compliant event dict

        Returns:
            dict
        """
        return {
            'sensor': self.sensor_id,
            'sendTime': convert_datetime_to_iso(datetime.now(UTC)),
            'data': event,
            'dataVersion': CALIPER_EVENT_CONTEXT
        }
