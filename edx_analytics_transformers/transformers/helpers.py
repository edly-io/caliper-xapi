"""
Common helper methods for transformers
"""
from logging import getLogger

from django.contrib.auth import get_user_model

from lms.djangoapps.courseware.courses import get_course_by_id
from opaque_keys.edx.keys import CourseKey
from student.models import anonymous_id_for_user    # pylint: disable=import-error


logger = getLogger(__name__)
User = get_user_model()


def get_anonymous_user_id_by_username(username, course_id=None):
    """
    Generate anonymous user id.

    Generate anonymous id as per course if `course_id` is provided. Otherwise
    generate anonymous id as per student.
    If no anonymous id is generated, return "anonymous".

    Arguments:
        username (str):     username for the learner
        course_id (str):    course key string.

    Returns:
        str
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        logger.info('User with username "%s" does not exist. '
                    'Cannot generate anonymous ID', username)

        anonymous_id = 'anonymous'
    else:
        anonymous_id = anonymous_id_for_user(user, course_id)

    return anonymous_id


def get_course_from_id(course_id):
    """
    Get Course object using the `course_id`

    Arguments:
        course_id (str) :   ID of the course

    Returns:
        `Course`
    """
    # TODO: Add caching
    course_key = CourseKey.from_string(course_id)
    return get_course_by_id(course_key)
