"""
Test Cases for helpers
"""
import json
from datetime import datetime, date
from unittest import TestCase

import ddt
from pytz import UTC

from edx_analytics_transformers.backends.caliper import CaliperBackend
from edx_analytics_transformers.backends.xapi import XAPIBackend
from edx_analytics_transformers.helpers import GenericJSONEncoder, BackendJSONDecoder


DATETIME = datetime(2020, 1, 1, 0, 0, 0)
DATETIME_WITH_TZ_INFO = DATETIME.replace(tzinfo=UTC)
DATE = date(2020, 1, 1)

OBJECT_TYPES = [
    CaliperBackend(),
    XAPIBackend(),
    DATETIME,
    DATETIME_WITH_TZ_INFO,
    DATE,
    'string',
    1000
]


def _make_backend_dict_json(backend_name):
    return json.dumps({
        'type': backend_name,
        'dict': {}
    })


@ddt.ddt
class TestGenericJSONEncoder(TestCase):
    """Test GenericJSONEncoder with different object types"""

    @ddt.data(
        (CaliperBackend(), _make_backend_dict_json('CaliperBackend')),
        (XAPIBackend(), _make_backend_dict_json('XAPIBackend')),
        (DATETIME, '"2020-01-01T00:00:00+00:00"'),
        (DATETIME_WITH_TZ_INFO, '"2020-01-01T00:00:00+00:00"'),
        (DATE, '"2020-01-01"'),
        ('string', '"string"'),
        (1000, '1000'),
    )
    @ ddt.unpack
    def test_encoding_of_different_objects(self, data, expected_output):
        encoded = json.dumps(data, cls=GenericJSONEncoder)
        self.assertEqual(encoded, expected_output)


@ddt.ddt
class TestBackendJSONDecoder(TestCase):
    """Test BackendJSONDecoder with two supported backends"""

    @ddt.data(
        'CaliperBackend',
        'XAPIBackend',
    )
    def test_backends_decoding(self, backend):
        BACKEND_MAP = {
            'CaliperBackend': CaliperBackend,
            'XAPIBackend': XAPIBackend
        }
        backend_json = json.dumps({
            'type': backend,
            'dict': {}
        })
        json_decoded_backend = json.loads(backend_json, cls=BackendJSONDecoder)
        self.assertTrue(isinstance(json_decoded_backend, BACKEND_MAP[backend]))
