"""
Tests for celery tasks
"""
import json

import ddt
from django.test import TestCase
from mock import MagicMock, patch, sentinel

from edx_analytics_transformers.django.tests.factories import RegExFilterFactory
from edx_analytics_transformers.tasks import async_send


@ddt.ddt
class TestAsyncSend(TestCase):
    """Test async_send task"""

    def setUp(self):
        super(TestAsyncSend, self).setUp()
        self.event = {
            'name': str(sentinel.name),
            'event_type': 'edx.test.event',
            'time': '2020-01-01T12:12:12.000000+00:00',
            'event': {
                'key': 'value'
            },
            'session': '0000'
        }

        self.backend_dict = {
            'type': 'AnyBackend',
            'dict': {}
        }
        self.backend_name = 'test'
        self.mocked_backend = MagicMock()

    def test_with_error_in_decoding_backend(self):
        with patch('edx_analytics_transformers.tasks.json.loads', side_effect=[self.event, ValueError]):
            async_send(json.dumps(self.backend_dict), json.dumps(self.event), self.backend_name)

        self.mocked_backend.send.assert_not_called()

    @patch('edx_analytics_transformers.tasks.logger')
    def test_with_no_or_disabled_filter_for_backend(self, mocked_logger):
        with patch('edx_analytics_transformers.tasks.json.loads', side_effect=[
            self.event, self.mocked_backend
        ]):
            async_send(json.dumps(self.backend_dict), json.dumps(self.event), self.backend_name)

        mocked_logger.warning.assert_called_once_with(
            'Regular Expression Filter does not have any enabled configurations'
            ' for backend "%s". Allowing the event "%s" to pass through.',
            self.backend_name, str(sentinel.name)
        )
        self.mocked_backend.send.assert_called_once_with(self.event)

    @patch('edx_analytics_transformers.tasks.logger')
    @ddt.data(
        ('sentinel.* \n will_match', 'whitelist', True),
        ('nope \n will_not_match', 'whitelist', False),
    )
    @ddt.unpack
    def test_with_enabled_filter_for_backend(self, regex_string, filter_type, should_pass_test, mocked_logger):
        event_name = str(sentinel.name)
        RegExFilterFactory.create(
            backend_name=self.backend_name,
            is_enabled=True,
            filter_type=filter_type,
            regular_expressions=regex_string
        )
        with patch('edx_analytics_transformers.tasks.json.loads', side_effect=[
            self.event, self.mocked_backend
        ]):
            async_send(json.dumps(self.backend_dict), json.dumps(self.event), self.backend_name)

        if should_pass_test:
            mocked_logger.info.assert_called_once_with(
                'Event "%s" is allowed to be processed by backend "%s"',
                event_name, self.backend_name
            )
            self.mocked_backend.send.assert_called_once_with(self.event)

        else:
            mocked_logger.info.assert_called_once_with(
                'Event "%s" is not allowed to be processed by backend "%s"',
                event_name, self.backend_name
            )
            self.mocked_backend.send.assert_not_called()

    def test_successful_sending_event_to_backend(self):
        with patch('edx_analytics_transformers.tasks.json.loads', side_effect=[
            self.event, self.mocked_backend
        ]):
            async_send(json.dumps(self.backend_dict), json.dumps(self.event), self.backend_name)

        self.mocked_backend.send.assert_called_once_with(self.event)
