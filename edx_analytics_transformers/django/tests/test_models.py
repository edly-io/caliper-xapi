"""
Test the django models
"""
import ddt
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from mock import call, patch

from edx_django_utils.cache import TieredCache

from edx_analytics_transformers.django.tests.factories import RouterConfigurationFactory
from edx_analytics_transformers.django.models import RouterConfiguration
from edx_analytics_transformers.django.tests import FROZEN_UUID


@ddt.ddt
class TestRouterConfiguration(TestCase):
    """
    Test `RouterConfiguration` model
    """

    def setUp(self):
        super(TestRouterConfiguration, self).setUp()
        TieredCache.dangerous_clear_all_tiers()

    def test_clean_method_unique_constraints(self):
        router = None

        # test when `enterprise_uuid` is null
        # unique_together contraint does not apply to `null` values so we have to
        # validate using `clean method`.
        # `clean` method is called only for form submissions (e.g. from Admin panel)
        # therefore we have to manually call it for testing
        for _ in range(2):
            router = RouterConfigurationFactory(
                configurations='{}',
                is_enabled=True,
                backend_name='first'
            )

        with self.assertRaises(ValidationError):

            router.clean()

        # test when `enterprise_uuid` is not null
        # unique_together contraint will fail in the following case.
        router = RouterConfigurationFactory(
            configurations='{}',
            is_enabled=True,
            enterprise_uuid=FROZEN_UUID,
            backend_name='first'
        )
        with self.assertRaises(IntegrityError):
            RouterConfigurationFactory(
                configurations='{}',
                is_enabled=True,
                enterprise_uuid=FROZEN_UUID,
                backend_name='first'
            )

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
        mocked_objects_get.assert_called_once_with(is_enabled=True, enterprise_uuid=None, backend_name='first')
        self.assertIn(
            call('No router was found in cache for backend "%s" and enterprise "%s"', 'first', None),
            mocked_logger.debug.mock_calls
        )

        self.assertIn(
            call('Router has been stored in cache for backend "%s" and enterprise "%s"', 'first', None),
            mocked_logger.debug.mock_calls
        )

        mocked_logger.reset_mock()
        mocked_objects_get.reset_mock()

        router = RouterConfiguration.get_enabled_router(backend_name='first')
        mocked_objects_get.assert_not_called()
        mocked_logger.debug.assert_called_once_with(
            'Router is found in cache for backend "%s" and enterprise "%s"',
            'first', None
        )

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
