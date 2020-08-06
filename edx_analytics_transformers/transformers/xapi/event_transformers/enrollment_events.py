"""
Transformers for enrollment related events.
"""
from logging import getLogger

from django.conf import settings
from django.urls import reverse

from tincan import (
    Activity,
    ActivityDefinition,
    Context,
    LanguageMap,
    Verb,
    Extensions
)

# from edx_analytics_transformers.transformers.helpers import get_anonymous_user_id_by_username
from edx_analytics_transformers.transformers.helpers import get_course_from_id
from edx_analytics_transformers.transformers.xapi import constants
from edx_analytics_transformers.transformers.xapi.registry import XApiTransformersRegistry
from edx_analytics_transformers.transformers.xapi.transformer import XApiTransformer


logger = getLogger(__name__)


class BaseEnrollmentTransformer(XApiTransformer):
    """
    Base transformer for enrollment events.
    """
    additional_fields = ('context', )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        course_id = self.find_nested('course_id')
        # TODO: make a method to get course URL. and use that everywhere
        object_id = '{root_url}{course_root_url}'.format(
                    root_url=settings.LMS_ROOT_URL,
                    course_root_url=reverse('course_root', kwargs={
                        'course_id': course_id
                    })
        )

        course = get_course_from_id(course_id)
        display_name = course.display_name

        return Activity(
            id=object_id,
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_COURSE,
                name=LanguageMap({constants.EN: display_name}),
            ),
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """
        return Context(
            # FIXME: registration must be a UUID
            # registration=get_anonymous_user_id_by_username(
            #     self.event['context']['username'],
            #     self.event['context']['course_id']
            # ),
            extensions=Extensions({
                constants.XAPI_CONTEXT_REFERRER: self.event['context']['referer'],
            })
        )


@XApiTransformersRegistry.register('edx.course.enrollment.activated')
class EnrollmentActivatedTransformer(BaseEnrollmentTransformer):
    """
    Transformers for event generated when learner enrolls in a course.
    """
    verb = Verb(
        id=constants.XAPI_VERB_REGISTERED,
        display=LanguageMap({constants.EN: constants.REGISTERED}),
    )


@XApiTransformersRegistry.register('edx.course.enrollment.deactivated')
class EnrollmentDeactivatedTransformer(BaseEnrollmentTransformer):
    """
    Transformers for event generated when learner un-enrolls from a course.
    """
    verb = Verb(
        id=constants.XAPI_VERB_UNREGISTERED,
        display=LanguageMap({constants.EN: constants.UNREGISTERED}),
    )
