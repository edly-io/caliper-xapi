"""
Test the RequestsRouter.
"""
from django.test import TestCase
from mock import MagicMock, call, patch, sentinel

from eventtracking.processors.exceptions import EventEmissionExit

from edx_analytics_transformers.utils.http_client import HttpClient
from edx_analytics_transformers.routers.requests_router import RequestsRouter
from edx_analytics_transformers.django.tests.factories import RouterConfigurationFactory


ROUTER_CONFIG_FIXTURE = [
    {
        'router_type': 'AUTH_HEADERS',
        'match_params': {
            'data.key': 'value'
        },
        'host_configurations': {
            'url': 'http://test1.com',
            'headers': {},
            'auth_scheme': 'Bearer',
            'auth_key': 'test_key'
        },
        'override_args': {
            'new_key': 'new_value'
        }
    },
    {
        'router_type': 'OAUTH2',
        'match_params': {
            'non_existing.id.value': 'test'
        },
        'host_configurations': {
            'url': 'http://test2.com',
            'client_id': 'id',
            'client_secret': 'secret'
        },
        'override_args': {}
    },
    {
        'router_type': 'API_KEY',
        'match_params': {
            'event_type': 'edx.test.event'
        },
        'host_configurations': {
            'url': 'http://test3.com',
            'api_key': 'test_key'
        }
    },
]


class TestRequestsRouter(TestCase):
    """
    Test the RequestsRouter
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
            'session': '0000'
        }

        self.transformed_event = {
            'name': str(sentinel.name),
            'transformed': True,
            'event_time': '2020-01-01T12:12:12.000000+00:00',
            'data': {
                'key': 'value'
            },
        }

        self.router = RequestsRouter(processors=[], backend_name='test')

    @patch('edx_analytics_transformers.utils.http_client.requests.post')
    @patch('edx_analytics_transformers.routers.requests_router.logger')
    def test_with_processor_exception(self, mocked_logger, mocked_post):
        processors = [
            MagicMock(return_value=self.transformed_event),
            MagicMock(side_effect=EventEmissionExit, return_value=self.transformed_event),
            MagicMock(return_value=self.transformed_event),
        ]
        processors[1].side_effect = EventEmissionExit

        router = RequestsRouter(processors=processors, backend_name='test')
        router.send(self.sample_event, self.transformed_event)

        processors[0].assert_called_once_with(self.transformed_event)
        processors[1].assert_called_once_with(self.transformed_event)
        processors[2].assert_not_called()

        mocked_post.assert_not_called()

        self.assertIn(call(
            'Could not process event %s for backend %s\'s router',
            self.sample_event['name'],
            'test',
            exc_info=True
        ), mocked_logger.info.mock_calls)

    @patch('edx_analytics_transformers.utils.http_client.requests.post')
    @patch('edx_analytics_transformers.routers.requests_router.logger')
    def test_with_no_router_configurations_available(self, mocked_logger, mocked_post):
        router = RequestsRouter(processors=[], backend_name='test')
        router.send(self.sample_event, self.transformed_event)

        mocked_post.assert_not_called()

        self.assertIn(
            call('Could not find an enabled router configurations for backend %s', 'test'),
            mocked_logger.info.mock_calls
        )

    @patch('edx_analytics_transformers.utils.http_client.requests.post')
    @patch('edx_analytics_transformers.routers.requests_router.logger')
    def test_with_no_available_hosts(self, mocked_logger, mocked_post):
        RouterConfigurationFactory.create(
            backend_name='test_backend',
            is_enabled=True,
            configurations=ROUTER_CONFIG_FIXTURE[1:1]
        )

        router = RequestsRouter(processors=[], backend_name='test_backend')
        router.send(self.sample_event, self.transformed_event)

        mocked_post.assert_not_called()

        self.assertIn(
            call(
                'Event %s is not allowed to be sent to any host for router with backend "%s"',
                self.sample_event['name'], 'test_backend'
            ),
            mocked_logger.info.mock_calls
        )

    @patch('edx_analytics_transformers.utils.http_client.requests.post')
    def test_successful_routing_of_event(self, mocked_post):
        mocked_oauth_client = MagicMock()
        mocked_api_key_client = MagicMock()

        MOCKED_MAP = {
            'AUTH_HEADERS': HttpClient,
            'OAUTH2': mocked_oauth_client,
            'API_KEY': mocked_api_key_client
        }

        RouterConfigurationFactory.create(
            backend_name='test_routing',
            is_enabled=True,
            configurations=ROUTER_CONFIG_FIXTURE
        )

        router = RequestsRouter(processors=[], backend_name='test_routing')

        with patch.dict('edx_analytics_transformers.routers.requests_router.ROUTER_STRATEGY_MAPPING', MOCKED_MAP):
            router.send(self.sample_event, self.transformed_event)

        # test the HTTP client
        overridden_event = self.transformed_event.copy()
        overridden_event['new_key'] = 'new_value'

        mocked_post.assert_has_calls([
            call(
                ROUTER_CONFIG_FIXTURE[0]['host_configurations']['url'],
                json=overridden_event,
                headers={
                    'Authorization': 'Bearer test_key'
                }
            ),
        ])

        # test mocked api key client
        mocked_api_key_client.assert_has_calls([
            call(**ROUTER_CONFIG_FIXTURE[2]['host_configurations']),
            call().send(self.transformed_event)
        ])

        # test mocked oauth client
        mocked_oauth_client.assert_not_called()
