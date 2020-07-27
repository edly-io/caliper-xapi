"""
Test the wrapper processor
"""
from unittest import TestCase

from mock import sentinel

from edx_analytics_transformers.processors.wrapper_processor import WrapperProcessor


class TestWrapperProcessor(TestCase):
    """
    Test the wrapper processor
    """

    def setUp(self):
        super().setUp()
        self.sample_event = {
            'name': str(sentinel.name)
        }

    def test_wrapper_processor(self):
        result = WrapperProcessor()(self.sample_event)
        self.assertEqual(result, {
            'WRAPPED': self.sample_event
        })
