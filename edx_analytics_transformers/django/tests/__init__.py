"""
Execute the tasks required before running the tests.
"""

import sys

import mock


def _mock_third_party_modules():
    """
    Mock third party modules used in the app.
    """
    student_module = mock.MagicMock()
    student_module.anonymous_id_for_user.return_value = 'anonymous_id'
    sys.modules['student.models'] = student_module


_mock_third_party_modules()
