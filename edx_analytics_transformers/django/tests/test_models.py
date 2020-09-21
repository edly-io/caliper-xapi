"""
Test the django models
"""
import ddt
from mock import call, patch
from django.test import TestCase

from edx_django_utils.cache import TieredCache

from edx_analytics_transformers.django.tests.factories import RouterConfigurationFactory
from edx_analytics_transformers.django.models import RouterConfiguration


@ddt.ddt
class TestRouterConfiguration(TestCase):
    """
    Test `RouterConfiguration` model
    """

    def setUp(self):
        super(TestRouterConfiguration, self).setUp()
        TieredCache.dangerous_clear_all_tiers()

    @patch('edx_analytics_transformers.django.models.RouterConfiguration.objects.get',
           side_effect=RouterConfiguration.objects.get)
    @patch('edx_analytics_transformers.django.models.logger')
    def test_router_caching(self, mocked_logger, mocked_objects_get):
        first_router = RouterConfigurationFactory(
            configurations='{}',
            is_enabled=True,
            backend_name='first'
        )

        router = RouterConfiguration.get_enabled_router(backend_name='first')

        self.assertEqual(router, first_router)
        mocked_objects_get.assert_called_once_with(is_enabled=True, backend_name='first')
        self.assertIn(
            call('No router was found in cache for backend "%s"', 'first'),
            mocked_logger.debug.mock_calls
        )

        self.assertIn(
            call('Router has been stored in cache for backend "%s"', 'first'),
            mocked_logger.debug.mock_calls
        )

        mocked_logger.reset_mock()
        mocked_objects_get.reset_mock()

        router = RouterConfiguration.get_enabled_router(backend_name='first')
        mocked_objects_get.assert_not_called()
        mocked_logger.debug.assert_called_once_with('Router is found in cache for backend "%s"', 'first')

        self.assertEqual(router, first_router)

    def test_allowed_hosts(self):
        config_fixture = [
            {
                'match_params': {
                    'context.org_id': 'test'
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
            }
        ]

        original_event = {
            'context': {
                'org_id': 'test'
            },
            'data': {
                'id': 'test_id'
            }
        }

        router = RouterConfigurationFactory(
            configurations=config_fixture,
            is_enabled=True,
            backend_name='first'
        )

        hosts = router.get_allowed_hosts(original_event)
        self.assertEqual(config_fixture[:1], hosts)
