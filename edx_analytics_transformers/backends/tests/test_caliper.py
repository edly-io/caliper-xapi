"""
Test the caliper backend.
"""

from __future__ import absolute_import

import json
from unittest import TestCase

from mock import ANY, MagicMock, call, patch, sentinel

from edx_analytics_transformers.backends.caliper import CaliperBackend


class TestCaliperBackend(TestCase):
    """Test cases for Caliper backend"""

    def setUp(self):
        super(TestCaliperBackend, self).setUp()
        self.sample_event = {
            'name': str(sentinel.name)
        }
        self.routers = {
            '0': MagicMock(),
            '1': MagicMock(),
        }

        self.backend = CaliperBackend(routers=self.routers)

    @patch('edx_analytics_transformers.backends.base_transformer_backend.logger')
    def test_send_method_with_no_transformer_implemented(self, mocked_logger):
        self.backend.send(self.sample_event)
        mocked_logger.error.assert_called_once_with(
            'Could not get transformer for %s event.',
            self.sample_event.get('name')
        )

    @patch(
        'edx_analytics_transformers.backends.caliper.CaliperTransformersRegistry.get_transformer',
        side_effect=ValueError
    )
    @patch('edx_analytics_transformers.backends.base_transformer_backend.logger')
    def test_send_method_with_unknown_exception(self, mocked_logger, _):
        with self.assertRaises(ValueError):
            self.backend.send(self.sample_event)

        mocked_logger.exception.assert_called_once_with(
            'There was an error while trying to transform event "%s" using %s backend.'
            ' Error: %s', 'sentinel.name', 'CaliperBackend', ANY
        )

    @patch('edx_analytics_transformers.backends.caliper.CaliperTransformersRegistry.get_transformer')
    @patch('edx_analytics_transformers.backends.caliper.caliper_logger')
    def test_send_method_with_successfull_flow(self, mocked_logger, mocked_get_transformer):
        transformed_event = {
            'transformed_key': 'transformed_value'
        }
        mocked_transformer = MagicMock()
        mocked_transformer.transform.return_value = transformed_event
        mocked_get_transformer.return_value = mocked_transformer

        self.backend.send(self.sample_event)

        self.assertIn(call(json.dumps(transformed_event)), mocked_logger.mock_calls)

        for _, router in self.routers.items():
            router.send.assert_called_once_with(self.sample_event, transformed_event)
