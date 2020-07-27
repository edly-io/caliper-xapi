"""
Caliper event processing backend
"""
import json
from logging import getLogger

from edx_analytics_transformers.transformers.caliper.registry import TransformerRegistry
from edx_analytics_transformers.transformers.caliper.exceptions import NoTransformerImplemented

logger = getLogger(__name__)


class CaliperBackend:
    """
    Backend to transform events into xAPI compliant format
    and then route those events to configured endpoints.
    """

    def __init__(self, routers={}):     # pylint: disable=dangerous-default-value
        """
        Initialize CaliperBackend.

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
        Transform the event into IMS Caliper format.

        Arguments:
            event (dict):   Event to be transformed.

        Returns:
            dict:           transformed event

        Raises:
            Any Exception
        """
        event_name = event.get('name')
        logger.info('Going to transform event "%s" into Caliper format', event_name)

        try:
            transformed_event = TransformerRegistry.get_transformer(event).transform()

        except NoTransformerImplemented:
            logger.error('Could not get transformer for %s event.', event.get('name'))
            return None

        except Exception as ex:
            logger.exception(
                'There was an error while trying to transform event "%s" into'
                ' Caliper format. Error: %s', event_name, ex)
            raise

        logger.info(
            'Successfully transformed event "%s" into Caliper format',
            event_name
        )
        logger.info(json.dumps(transformed_event))
        return transformed_event

    def route_event(self, original_event, transformed_event):
        """
        Router the event through the configured routers.

        Arguments:
            event (dict):   Event to be delivered.
        """
        for name, router in self.routers.items():
            logger.info('Routing event to router %s', name)
            router.send(original_event, transformed_event)
