"""
Caliper backend for transforming and routing events.
"""
import json
from logging import getLogger

from edx_analytics_transformers.backends.base_transformer_backend import BaseTransformerBackend
from edx_analytics_transformers.transformers.caliper.registry import CaliperTransformersRegistry


caliper_logger = getLogger('caliper_tracking')


class CaliperBackend(BaseTransformerBackend):
    """
    Caliper backend for transforming and routing events.

    This backend first transform the event using the registered transformer
    and then route the events through the configured routers.

    Every router configured to be used MUST support the transfromed event type.
    """

    registry = CaliperTransformersRegistry

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
        transformed_event = super(CaliperBackend, self).transform_event(event)

        if transformed_event:
            caliper_logger.info(json.dumps(transformed_event))

        return transformed_event
