"""
Test the EnterpriseContextProvider.
"""
from datetime import datetime

from django.test import TestCase
from mock import patch, sentinel
from pytz import UTC

from edx_analytics_transformers.django.tests.factories import UserFactory
from edx_analytics_transformers.processors.enterprise_processors import EnterpriseContextProvider
from edx_analytics_transformers.django.tests import FROZEN_UUID


FROZEN_TIME = datetime(2013, 10, 3, 8, 24, 55, tzinfo=UTC)


class TestEnterpriseContextProvider(TestCase):
    """
    Test the EnterpriseContextProvider.
    """

    def setUp(self):
        super().setUp()
        self.sample_event = {
            'name': str(sentinel.name),
            'event_type': 'edx.test.event',
            'time': '2020-01-01T12:12:12.000000+00:00',
            'data': {
                'key': 'value'
            },
            'context': {
                'username': 'testuser'
            },
            'session': '0000'
        }

    @patch('edx_analytics_transformers.processors.enterprise_processors.enterprise_enabled', return_value=False)
    @patch('edx_analytics_transformers.processors.enterprise_processors.EnterpriseApiClient')
    def test_with_enterprise_disabled(self, mocked_api_client, _):
        result = EnterpriseContextProvider()(self.sample_event)
        self.assertDictEqual(result, self.sample_event)
        mocked_api_client.assert_not_called()

    @patch('edx_analytics_transformers.processors.enterprise_processors.EnterpriseApiClient')
    def test_with_no_user_in_event(self, mocked_api_client):
        sample_event = self.sample_event.copy()
        sample_event['context']['username'] = ''
        result = EnterpriseContextProvider()(self.sample_event)
        self.assertDictEqual(result, self.sample_event)
        mocked_api_client.assert_not_called()

    @patch('edx_analytics_transformers.processors.enterprise_processors.EnterpriseApiClient')
    def test_with_user_not_found(self, mocked_api_client):
        result = EnterpriseContextProvider()(self.sample_event)
        self.assertDictEqual(result, self.sample_event)
        mocked_api_client.assert_not_called()

    @patch('edx_analytics_transformers.processors.enterprise_processors.EnterpriseApiClient', side_effect=Exception)
    def test_with_generic_exception(self, mocked_api_client):
        user = UserFactory(username='testuser')
        result = EnterpriseContextProvider()(self.sample_event)
        mocked_api_client.assert_called_once_with(user=user)
        self.assertDictEqual(result, self.sample_event)

    @patch('edx_analytics_transformers.processors.enterprise_processors.EnterpriseApiClient')
    def test_successful_processing(self, mocked_api_client):
        user = UserFactory(username='testuser')
        result = EnterpriseContextProvider()(self.sample_event)
        mocked_api_client.assert_called_once_with(user=user)
        expected = self.sample_event.copy()
        expected['context']['enterprise_uuid'] = FROZEN_UUID
        self.assertDictEqual(result, self.sample_event)
