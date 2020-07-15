"""
Configure pytest before running any test.
"""
import sys

import mock


def pytest_configure(config):
    """
    Mock third party modules that are going to be used in the app.
    """
    config.mocked_modules = []

    student_module = mock.MagicMock()
    student_module.anonymous_id_for_user.return_value = 'anonymous_id'
    sys.modules['student.models'] = student_module
