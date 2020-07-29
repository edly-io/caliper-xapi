"""
Test the RequestsRouter
"""
from django.test import TestCase
from mock import MagicMock, call, patch, sentinel

from eventtracking.processors.exceptions import EventEmissionExit

from edx_analytics_transformers.routers.requests_router import RequestsRouter
from edx_analytics_transformers.django.tests.factories import RouterConfigurationsFactory


ROUTER_CONFIG_FIXTURE = [
    {
        'match_params': {
            'data.key': 'value'
        },
        'host_configurations': {
            'URL': 'http://test1.com',
            'HEADERS': {},
            'AUTH_SCHEME': 'Bearer',
            'API_KEY': 'test_key'
        },
        'override_args': {
            'new_key': 'new_value'
        }
    },
    {
        'match_params': {
            'non_existing.id.value': 'test'
        },
        'host_configurations': {
            'URL': 'http://test2.com',
            'HEADERS': {},
            'AUTH_SCHEME': 'Bearer',
            'API_KEY': 'test_key'
        },
        'override_args': {}
    },
    {
        'match_params': {
            'event_type': 'edx.test.event'
        },
        'host_configurations': {
            'URL': 'http://test3.com',
            'HEADERS': {},
            'AUTH_SCHEME': 'Bearer',
            'API_KEY': 'test_key'
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
        RouterConfigurationsFactory.create(
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

        def _make_headers(host_config):
            headers = host_config['HEADERS']
            headers['Authorization'] = '{} {}'.format(
                host_config['AUTH_SCHEME'],
                host_config['API_KEY']
            )
            return headers

        RouterConfigurationsFactory.create(
            backend_name='test_routing',
            is_enabled=True,
            configurations=ROUTER_CONFIG_FIXTURE
        )

        router = RequestsRouter(processors=[], backend_name='test_routing')
        router.send(self.sample_event, self.transformed_event)

        host_0_expected_event = self.transformed_event.copy()
        host_0_expected_event['new_key'] = 'new_value'

        headers = [
            _make_headers(host['host_configurations']) for host in ROUTER_CONFIG_FIXTURE
        ]

        mocked_post.assert_has_calls([
            call(
                ROUTER_CONFIG_FIXTURE[0]['host_configurations']['URL'],
                json=host_0_expected_event,
                headers=headers[0]
            ),
            call(
                ROUTER_CONFIG_FIXTURE[2]['host_configurations']['URL'],
                json=self.transformed_event,
                headers=headers[2]
            ),
        ])

        self.assertNotIn(
            call(
                ROUTER_CONFIG_FIXTURE[1]['host_configurations']['URL'],
                json=self.transformed_event,
                headers=headers[1]
            ),
            mocked_post.mock_calls
        )
