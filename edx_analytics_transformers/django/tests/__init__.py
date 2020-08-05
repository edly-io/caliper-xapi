"""
Execute the tasks required before running the tests.
"""

import sys

import mock


def _mock_third_party_modules():
    """
    Mock third party modules used in the app.
    """
    # TODO: add these modules as dummy modules?
    # mock student module
    student_module = mock.MagicMock()
    student_module.anonymous_id_for_user.return_value = 'anonymous_id'
    sys.modules['student.models'] = student_module

    # mock courseware module
    mocked_course = mock.MagicMock()
    mocked_course.display_name = 'Demonstration Course'

    mocked_courses = mock.MagicMock()
    mocked_courses.get_course_by_id.return_value = mocked_course
    sys.modules['lms.djangoapps.courseware.courses'] = mocked_courses

    # mock opaque keys module
    mocked_keys = mock.MagicMock()
    sys.modules['opaque_keys.edx.keys'] = mocked_keys


_mock_third_party_modules()
