"""
Base statement class for xAPI statements.
"""
from abc import abstractmethod
from logging import getLogger

from tincan import Activity, ActivityDefinition, Agent, LanguageMap, Statement, Context


logger = getLogger(__name__)


class BaseStatement(Statement):
    """
    Base statement class for xAPI statements.
    """

    def __init__(self, event, *args, **kwargs):
        """
        Initialize an xAPI Statement from a tracking log event.
        """
        try:
            kwargs.update(
                actor=self.get_actor(event),
                verb=self.get_verb(event),
                object=self.get_object(event),
                result=self.get_result(event),
                context=self.get_context(event),
                timestamp=self.get_timestamp(event)
            )
            super(BaseStatement, self).__init__(*args, **kwargs)

        except (ValueError, TypeError, AttributeError):
            message = "[XAPI] Could not generate Statement from class {}.".format(
                str(self.__class__))
            logger.error(message, exc_info=True)

    @abstractmethod
    def get_verb(self, _event):
        """
        get verb
        """

    def get_actor(self, _event):
        return Agent(
            name='test_user',
        )

    def get_object(self, _event):
        xapi_activity_id = 'test'
        X_API_ACTIVITY_COURSE = 'course'
        name = 'course a'
        description = 'testing'
        xapi_object_extensions = {}
        return Activity(
            id=xapi_activity_id,
            definition=ActivityDefinition(
                type=X_API_ACTIVITY_COURSE,
                name=LanguageMap({'en-US': name}),
                description=LanguageMap({'en-US': description}),
                extensions=xapi_object_extensions,
            ),
        )

    def get_context(self, _event):
        """Get Context for the statement."""
        return Context(
            platform='TESTING',
            # registration=self._get_enrollment_id(event) TODO: not sure why this format doesn't work
        )

    def get_timestamp(self, event):
        """Get the Timestamp for the statement."""
        return event['time']

    def get_result(self, _event):
        # Not all activities have a result.
        return None
