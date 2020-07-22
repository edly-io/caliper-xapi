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
    def __init__(self, routers={}):
        self.routers = routers

    def send(self, event):
        """
        Process the passed event.
        """
        transformed_event = self.transform_event(event)
        if transformed_event:
            self.route_event(event, transformed_event)

    def transform_event(self, event):
        event_name = event.get('name')
        logger.info('Going to transform event "%s" into Caliper format', event_name)

        try:
            transformed_event = TransformerRegistry.get_transformer(event).transform()
        except NoTransformerImplemented:
            logger.error('Could not get transformer for %s event.', event.get('name'))
            return
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
        for name, router in self.routers.items():
            logger.info('Routing event to router %s', name)
            router.send(original_event, transformed_event)
