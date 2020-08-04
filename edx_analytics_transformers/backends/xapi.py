"""
XAPI backend for transforming and routing events.
"""
from logging import getLogger

from edx_analytics_transformers.backends.base_transformer_backend import BaseTransformerBackend
from edx_analytics_transformers.transformers.xapi.registry import XApiTransformersRegistry


xapi_logger = getLogger('xapi_tracking')
logger = getLogger(__name__)


class XApiBackend(BaseTransformerBackend):
    """
    Backend for transformation and routing of events as per
    xAPI specifications.
    """
    registry = XApiTransformersRegistry

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
        logger.info('before transforming %s', event['name'])
        import json
        logger.info(json.dumps(event))
        transformed_event = super(XApiBackend, self).transform_event(event)

        if transformed_event:
            xapi_logger.info(transformed_event.to_json())

        return transformed_event
