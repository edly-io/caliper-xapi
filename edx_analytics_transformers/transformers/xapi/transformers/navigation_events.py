"""
Transformers for navigation related events.
"""
from logging import getLogger

from django.conf import settings
from django.urls import reverse

from tincan import (
    Activity,
    ActivityDefinition,
    ActivityList,
    LanguageMap,
    Context,
    ContextActivities,
    Verb,
    Extensions
)

# from edx_analytics_transformers.transformers.helpers import get_anonymous_user_id_by_username
from edx_analytics_transformers.transformers.xapi import constants
from edx_analytics_transformers.transformers.xapi.registry import XApiTransformersRegistry
from edx_analytics_transformers.transformers.xapi.transformer import XApiTransformer


logger = getLogger(__name__)


TAB_EVENTS_VERB_MAP = {
    'edx.ui.lms.sequence.next_selected': {
        'id': constants.XAPI_VERB_TERMINATED,
        'display': constants.TERMINATED
    },
    'edx.ui.lms.sequence.previous_selected': {
        'id': constants.XAPI_VERB_TERMINATED,
        'display': constants.TERMINATED
    },
    'edx.ui.lms.sequence.tab_selected': {
        'id': constants.XAPI_VERB_INITIALIZED,
        'display': constants.INITIALIZED
    }
}


@XApiTransformersRegistry.register('edx.ui.lms.link_clicked')
class LinkClickedTransformer(XApiTransformer):
    """
    xAPI transformer for event generated when user clicks a link.
    """
    additional_fields = ('context', )

    verb = Verb(
        id=constants.XAPI_VERB_EXPERIENCED,
        display=LanguageMap({constants.EN: constants.EXPERIENCED})
    )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        return Activity(
            id=self.event['data']['target_url'],
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_LINK,
                # TODO: how to get link's display name?
                name=LanguageMap({constants.EN: 'Link name'}),
                extensions=Extensions({
                    constants.XAPI_ACTIVITY_POSITION: self.event['data']['target_url']
                })
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
            contextActivities=self.get_context_activities(),
            extensions=Extensions({
                constants.XAPI_CONTEXT_REFERRER: self.event['context']['referer'],
            })
        )

    def get_context_activities(self):
        """
        Get context activities for xAPI transformed event.

        Returns:
            `ContextActivities`
        """
        parent_activities = [
            Activity(
                id='{root_url}{course_root_url}'.format(
                    root_url=settings.LMS_ROOT_URL,
                    course_root_url=reverse('course_root', kwargs={
                        'course_id': self.event['context']['course_id']
                    }),
                ),
                object_type=constants.XAPI_ACTIVITY_COURSE
            ),
        ]
        return ContextActivities(
            parent=ActivityList(parent_activities),
        )


@ XApiTransformersRegistry.register('edx.ui.lms.sequence.outline.selected')
@ XApiTransformersRegistry.register('edx.ui.lms.outline.selected')
class OutlineSelectedTransformer(XApiTransformer):
    """
    xAPI transformer for Navigation events.
    """
    additional_fields = ('context', )

    verb = Verb(
        id=constants.XAPI_VERB_INITIALIZED,
        display=LanguageMap({constants.EN: constants.INITIALIZED})
    )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        return Activity(
            id=self.event['data']['target_url'],
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_MODULE,
                name=LanguageMap({constants.EN: self.find_nested('target_name')}),
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


@ XApiTransformersRegistry.register('edx.ui.lms.sequence.next_selected')
@ XApiTransformersRegistry.register('edx.ui.lms.sequence.previous_selected')
@ XApiTransformersRegistry.register('edx.ui.lms.sequence.tab_selected')
class TabNavigationTransformer(XApiTransformer):
    """
    xAPI transformer for Navigation events.
    """
    additional_fields = ('context', )

    def get_verb(self):
        """
        Get verb for xAPI transformed event.

        Returns:
            `Verb`
        """
        event_name = self.event['name']
        verb = TAB_EVENTS_VERB_MAP[event_name]

        return Verb(
            id=verb['id'],
            display=LanguageMap({constants.EN: verb['display']})
        )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        if self.event['name'] == 'edx.ui.lms.sequence.tab_selected':
            position = self.event['data']['target_tab']
        else:
            position = self.event['data']['current_tab']

        return Activity(
            id=self.event['data']['id'],
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_MODULE,
                extensions=Extensions({
                    constants.XAPI_ACTIVITY_POSITION: position
                })
            ),
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """
        event_name = self.event['name']
        if event_name == 'edx.ui.lms.sequence.tab_selected':
            extensions = Extensions({
                constants.XAPI_CONTEXT_STARTING_POSITION: self.event['data']['current_tab'],
            })
        elif event_name == 'edx.ui.lms.sequence.next_selected':
            extensions = Extensions({
                constants.XAPI_CONTEXT_ENDING_POSITION: 'next unit',
            })
        else:
            extensions = Extensions({
                constants.XAPI_CONTEXT_ENDING_POSITION: 'previous unit',
            })
        return Context(
            # FIXME: registration must be a UUID
            # registration=get_anonymous_user_id_by_username(
            #     self.event['context']['username'],
            #     self.event['context']['course_id']
            # ),
            contextActivities=self.get_context_activities(),
            extensions=extensions
        )

    def get_context_activities(self):
        """
        Get context activities for xAPI transformed event.

        Returns:
            `ContextActivities`
        """
        parent_activities = [
            Activity(
                id=self.event['data']['id'],
                object_type=constants.XAPI_ACTIVITY_MODULE
            ),
        ]
        return ContextActivities(
            parent=ActivityList(parent_activities),
        )
