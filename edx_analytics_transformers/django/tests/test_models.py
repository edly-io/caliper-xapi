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

    def test_get_latest_router(self):
        # With no existing filters, it should return None
        self.assertIsNone(RouterConfiguration.get_latest_enabled_router('test'))

        first_enabled = []
        first_disabled = []
        second_enabled = []
        second_disabled = []

        for _ in range(5):
            first_enabled.append(RouterConfigurationFactory(is_enabled=True, backend_name='first'))
            first_disabled.append(RouterConfigurationFactory(is_enabled=False, backend_name='first'))
            second_enabled.append(RouterConfigurationFactory(is_enabled=True, backend_name='second'))
            second_disabled.append(RouterConfigurationFactory(is_enabled=False, backend_name='second'))

        # test with backend name
        self.assertEqual(first_enabled[4], RouterConfiguration.get_latest_enabled_router('first'))

        # test enabling a filter
        first_disabled[2].is_enabled = True
        first_disabled[2].save()

        self.assertEqual(first_disabled[2], RouterConfiguration.get_latest_enabled_router('first'))
        self.assertEqual(second_enabled[4], RouterConfiguration.get_latest_enabled_router('second'))

        # test modifying an enabled filter
        second_enabled[1].save()

        self.assertEqual(first_disabled[2], RouterConfiguration.get_latest_enabled_router('first'))
        self.assertEqual(second_enabled[1], RouterConfiguration.get_latest_enabled_router('second'))

    @patch('edx_analytics_transformers.django.models.RouterConfiguration.objects.filter',
           side_effect=RouterConfiguration.objects.filter)
    @patch('edx_analytics_transformers.django.models.logger')
    def test_latest_router_caching(self, mocked_logger, mocked_objects_filter):
        first_router = RouterConfigurationFactory(
            configurations='{}',
            is_enabled=True,
            backend_name='first'
        )

        router = RouterConfiguration.get_latest_enabled_router(backend_name='first')

        self.assertEqual(router, first_router)
        mocked_objects_filter.assert_called_once_with(is_enabled=True, backend_name='first')
        self.assertIn(
            call('No router was found in cache for backend "%s"', 'first'),
            mocked_logger.info.mock_calls
        )

        self.assertIn(
            call('Router has been stored in cache for backend "%s"', 'first'),
            mocked_logger.info.mock_calls
        )

        mocked_logger.reset_mock()
        mocked_objects_filter.reset_mock()

        router = RouterConfiguration.get_latest_enabled_router(backend_name='first')
        mocked_objects_filter.assert_not_called()
        mocked_logger.info.assert_called_once_with('Router is found in cache for backend "%s"', 'first')

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
