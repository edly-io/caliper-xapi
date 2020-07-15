"""
Tests for django models
"""
import re

import ddt
from mock import patch, sentinel
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from edx_analytics_transformers.django.tests.factories import RegExFilterFactory
from edx_analytics_transformers.django.models import validate_regex_list, RegExFilter


@ddt.ddt
class TestRegExFilter(TestCase):
    """Test RegExFilter model"""

    def test_get_latest_filter(self):
        # With no existing filters, it should return None
        self.assertIsNone(RegExFilter.get_latest_enabled_filter())

        first_enabled = []
        first_disabled = []
        second_enabled = []
        second_disabled = []

        for _ in range(5):
            first_enabled.append(RegExFilterFactory(is_enabled=True, backend_name='first'))
            first_disabled.append(RegExFilterFactory(is_enabled=False, backend_name='first'))
            second_enabled.append(RegExFilterFactory(is_enabled=True, backend_name='second'))
            second_disabled.append(RegExFilterFactory(is_enabled=False, backend_name='second'))

        # test with no backend name
        self.assertEqual(second_enabled[4], RegExFilter.get_latest_enabled_filter())

        # test with backend backend name
        self.assertEqual(first_enabled[4], RegExFilter.get_latest_enabled_filter('first'))

        # test enabling a filter
        first_disabled[2].is_enabled = True
        first_disabled[2].save()
        self.assertEqual(first_disabled[2], RegExFilter.get_latest_enabled_filter())
        self.assertEqual(first_disabled[2], RegExFilter.get_latest_enabled_filter('first'))
        self.assertEqual(second_enabled[4], RegExFilter.get_latest_enabled_filter('second'))

        # test modifying an enabled filter
        second_enabled[1].save()
        self.assertEqual(second_enabled[1], RegExFilter.get_latest_enabled_filter())
        self.assertEqual(first_disabled[2], RegExFilter.get_latest_enabled_filter('first'))
        self.assertEqual(second_enabled[1], RegExFilter.get_latest_enabled_filter('second'))

    def test_validator(self):
        valid_expressions = ['abc', '.?[1-10]*']
        invalid_expressions = ['***', '*?*']
        expressions_string = ' \n '.join(valid_expressions+invalid_expressions)

        expected_error_message = 'The following invalid expressions must be corrected: {}'.format(
            ', '.join(invalid_expressions)
        )

        with self.assertRaisesMessage(ValidationError, expected_error_message):
            validate_regex_list(expressions_string)

    @patch('edx_analytics_transformers.django.models.logger')
    def test_with_invalid_regular_expressions(self, mocked_logger):
        invalid_regular_exressions = ['***', '*?*']
        valid_regular_expressions = ['abc', '.?[1-10]*']

        expressions_string = ' \n '.join(invalid_regular_exressions + valid_regular_expressions)
        regex_filter = RegExFilterFactory(
            regular_expressions=expressions_string
        )

        compiled_regular_expressions = regex_filter.compiled_expressions
        self.assertEqual(compiled_regular_expressions, [
            re.compile(ex) for ex in valid_regular_expressions
        ])
        mocked_logger.error.assert_called_once_with(
            'The following invalid expressions were found in the filter: %s',
            ', '.join(invalid_regular_exressions)
        )

    @ddt.data(
        ('whitelist', 'sentinel.* \n not_matching \n .*', True),
        ('whitelist', 'not_matching \n ** \n !@#$!@', False),
        ('whitelist', '', True),
        ('whitelist', None, None),
        ('blacklist', 'sentinel.* \n not_matching \n .*', False),
        ('blacklist', 'not_matching \n ** \n !@#$!@', True),
        ('blacklist', '', False),
        ('blacklist', None, None),
    )
    @ddt.unpack
    def test_string_passes_test(self, filter_type, regex, should_pass_test):
        def create_filter():
            return RegExFilterFactory.create(
                is_enabled=True,
                filter_type=filter_type,
                regular_expressions=regex
            )

        event_name = str(sentinel.name)

        if regex is None:
            with self.assertRaises(IntegrityError):
                create_filter()

        else:
            reg_filter = create_filter()
            actual_test_result = reg_filter.string_passes_test(event_name)
            self.assertEqual(actual_test_result, should_pass_test)
