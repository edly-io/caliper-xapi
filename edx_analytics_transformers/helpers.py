"""
Helper methods and classes for edx_analytics_transformers
"""
import json
from datetime import date, datetime
from pytz import UTC

from edx_analytics_transformers.backends.caliper import CaliperBackend
from edx_analytics_transformers.backends.xapi import XAPIBackend


class GenericJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that encodes asynchronous event backends and datetime objects to json.
    """
    def default(self, obj):  # pylint: disable=method-hidden,arguments-differ
        if isinstance(obj, CaliperBackend):
            return {"type": "CaliperBackend", "dict": obj.__dict__}
        elif isinstance(obj, XAPIBackend):
            return {"type": "XAPIBackend", "dict": obj.__dict__}
        elif isinstance(obj, datetime):
            if obj.tzinfo is None:
                # Localize to UTC naive datetime objects
                obj = UTC.localize(obj)     # pylint: disable=no-value-for-parameter
            else:
                # Convert to UTC datetime objects from other timezones
                obj = obj.astimezone(UTC)
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        else:
            return super(GenericJSONEncoder, self).default(obj)


class BackendJSONDecoder(json.JSONDecoder):
    """
    JSON decoder for asynchronous event backends
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):     # pylint: disable=method-hidden
        """
        Deserialize object into the appropriate backend.
        """
        if 'type' in obj:
            if obj['type'] == 'CaliperBackend':
                obj = CaliperBackend(**obj['dict'])
            elif obj['type'] == 'XAPIBackend':
                obj = XAPIBackend(**obj['dict'])
        return obj
