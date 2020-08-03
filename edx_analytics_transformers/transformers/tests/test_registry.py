"""
Test the transformers registry.
"""
from django.test import TestCase
from mock import MagicMock

from edx_analytics_transformers.transformers.exceptions import NoTransformerImplemented
from edx_analytics_transformers.transformers.registry import TransformerRegistry


class TestTransformerRegistry(TestCase):
    """
    Test the `TransformerRegistry`.
    """

    def test_exception_with_no_mapping(self):
        class RegistryWithNoMapping(TransformerRegistry):
            pass

        with self.assertRaises(AttributeError):
            RegistryWithNoMapping.register('key')(MagicMock())

    def test_exception_for_unregistered_transformer(self):
        with self.assertRaises(NoTransformerImplemented):
            TransformerRegistry.get_transformer({
                'name': 'test'
            })
