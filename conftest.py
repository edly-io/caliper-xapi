"""
Configure pytest before running any test.
"""
import sys

import mock


def pytest_configure(config):
    """
    Configure pytest before running any tests.

    Arguments:
        config: pytest config object
    """
    _mock_third_party_modules(config)
    _load_signals()


def _mock_third_party_modules(config):
    """
    Mock third party modules used in the app.

    Arguments:
        config: pytest config object
    """
    student_module = mock.MagicMock()
    student_module.anonymous_id_for_user.return_value = 'anonymous_id'
    sys.modules['student.models'] = student_module


def _load_signals():
    """
    Import signals to load and connect them.
    """
    # pylint: disable=import-outside-toplevel, unused-import
    from edx_analytics_transformers import signals
