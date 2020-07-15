"""
Caliper event processing backend
"""
import json
from celery.utils.log import get_task_logger

from edx_analytics_transformers.transformers.caliper.registry import TransformerRegistry
from edx_analytics_transformers.transformers.caliper.exceptions import NoTransformerImplemented

logger = get_task_logger(__name__)


class CaliperBackend:
    """
    Backend to transform events into xAPI compliant format
    and then route those events to configured endpoints.
    """

    def send(self, event):
        """
        Process the passed event.
        """
        logger.info('CALIER: before transformation')
        logger.info(json.dumps(event))

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
