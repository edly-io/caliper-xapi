"""
Test the RequestsRouter
"""
from django.test import TestCase
from mock import MagicMock, call, patch, sentinel

from eventtracking.processors.exceptions import EventEmissionExit

from edx_analytics_transformers.routers.requests_router import RequestsRouter
from edx_analytics_transformers.django.tests.factories import RouterConfigFilterFactory


ROUTER_CONFIG_FIXTURE = [
    {
        'match_params': {
            'data.key': 'value'
        },
        'host_configurations': {
            'url': 'http://test1.com',
            'headers': {
                'authorization': 'Token test'
            }
        }
    },
    {
        'match_params': {
            'non_existing.id.value': 'test'
        },
        'host_configurations': {
            'url': 'http://test2.com',
            'headers': {
                'authorization': 'Token test'
            }
        }
    },
    {
        'match_params': {
            'event_type': 'edx.test.event'
        },
        'host_configurations': {
            'url': 'http://test3.com',
            'headers': {
                'authorization': 'Token test'
            }
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

    @patch('edx_analytics_transformers.routers.requests_router.requests.post')
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

    @patch('edx_analytics_transformers.routers.requests_router.requests.post')
    @patch('edx_analytics_transformers.routers.requests_router.logger')
    def test_with_no_router_configurations_available(self, mocked_logger, mocked_post):
        router = RequestsRouter(processors=[], backend_name='test')
        router.send(self.sample_event, self.transformed_event)

        mocked_post.assert_not_called()

        self.assertIn(
            call('Could not find an enabled router configurations for backend %s', 'test'),
            mocked_logger.info.mock_calls
        )

    @patch('edx_analytics_transformers.routers.requests_router.requests.post')
    @patch('edx_analytics_transformers.routers.requests_router.logger')
    def test_with_no_available_hosts(self, mocked_logger, mocked_post):
        RouterConfigFilterFactory.create(
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

    @patch('edx_analytics_transformers.routers.requests_router.requests.post')
    def test_successful_routing_of_event(self, mocked_post):

        RouterConfigFilterFactory.create(
            backend_name='test_routing',
            is_enabled=True,
            configurations=ROUTER_CONFIG_FIXTURE
        )

        router = RequestsRouter(processors=[], backend_name='test_routing')
        router.send(self.sample_event, self.transformed_event)

        mocked_post.assert_has_calls([
            call(
                ROUTER_CONFIG_FIXTURE[0]['host_configurations']['url'],
                json=self.transformed_event,
                headers=ROUTER_CONFIG_FIXTURE[0]['host_configurations']['headers']
            ),
            call(
                ROUTER_CONFIG_FIXTURE[2]['host_configurations']['url'],
                json=self.transformed_event,
                headers=ROUTER_CONFIG_FIXTURE[2]['host_configurations']['headers']
            ),
        ])

        self.assertNotIn(
            call(
                ROUTER_CONFIG_FIXTURE[1]['host_configurations']['url'],
                json=self.transformed_event,
                headers=ROUTER_CONFIG_FIXTURE[1]['host_configurations']['headers']
            ),
            mocked_post.mock_calls
        )
