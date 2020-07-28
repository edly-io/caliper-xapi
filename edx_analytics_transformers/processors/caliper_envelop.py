"""
Envelope the caliper transformed event.
"""
from datetime import datetime

from edx_analytics_transformers.transformers.caliper.constants import CALIPER_EVENT_CONTEXT
from edx_analytics_transformers.transformers.caliper.helpers import convert_datetime


class CaliperEnvelopProcessor:
    """
    Envelope the caliper transformed event.
    """
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id

    def __call__(self, event, sensor_id=None):
        """
        Envelope the caliper transformed event.
        """
        return {
            'sensor': sensor_id or self.sensor_id,
            'sendTime': convert_datetime(str(datetime.now())),
            'data': event,
            'dataVersion': CALIPER_EVENT_CONTEXT
        }
