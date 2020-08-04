"""
Base backend for routing backends.
"""
from abc import abstractmethod
from logging import getLogger

from edx_analytics_transformers.transformers.exceptions import NoTransformerImplemented


logger = getLogger(__name__)


class BaseTransformerBackend:
    """
    Base backend for transformer backends.

    This backend is used to transform events into any standard format
    and then route those events to configured endpoints.
    """

    registry = None

    def __init__(self, routers={}):     # pylint: disable=dangerous-default-value
        """
        Initialize BaseRoutingBackend.

        Events, after transformation, will be sent to the routers for further
        routing of the events.

        Arguments:
            routers (dict):     Dict of router objects.
        """
        self.routers = routers

    def send(self, event):
        """
        Transform and then route the event to the configured routers.

        Arguments:
            event (dict):   Event to be transformed and delivered.
        """
        transformed_event = self.transform_event(event)
        if transformed_event:
            self.route_event(event, transformed_event)

    def transform_event(self, event):
        """
        Transform the event.

        Transformer method can return transformed event in any data structure format
        (dict or any custom class) but the configured router(s) MUST support it.

        Arguments:
            event (dict):   Event to be transformed.

        Returns:
            ANY:           transformed event
        """
        event_name = event.get('name')
        logger.info('Going to transform event "%s" using %s', event_name, self.__class__.__name__)

        try:
            transformed_event = self.get_transformed_event(event)

        except NoTransformerImplemented:
            logger.error('Could not get transformer for %s event.', event.get('name'))
            return None

        except Exception as ex:
            logger.exception(
                'There was an error while trying to transform event "%s" using'
                ' %s backned. Error: %s', event_name, self.__class__.__name__, ex)
            raise

        logger.info(
            'Successfully transformed event "%s" using %s',
            event_name, self.__class__.__name__
        )

        return transformed_event

    def get_transformed_event(self, event):
        """
        Transform the event using the class's registry.

        Making this a separate method so that subclasses can override
        this method if those class want to do it some otherway.

        Arguments:
            event (dict):   Event to be transformed.

        Returns:
            ANY:           transformed event

        Raises:
            NoTransformerImplemented
        """
        return self.registry.get_transformer(event).transform()

    def route_event(self, original_event, transformed_event):
        """
        Router the event through the configured routers.

        `transformed_event` can be in any data structure format (dict
        or any custom class) but the configured router(s) MUST support it.

        Arguments:
            original_event (dict):     Open edX un-processed event
            transformed_event (ANY):   Event to be delivered.
        """
        for name, router in self.routers.items():
            logger.info('Routing event to router %s', name)
            router.send(original_event, transformed_event)
