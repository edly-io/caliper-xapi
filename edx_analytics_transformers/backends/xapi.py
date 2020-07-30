"""
XAPI backend for transforming and routing events.
"""
import json
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
        transformed_event = super(XApiBackend, self).transform_event(event)

        if transformed_event:
            xapi_logger.info(json.dumps(transformed_event))

        return transformed_event

    # better
    # def get_transformed_event(self, event):
    #     # TODO: add a adapter method in statement class?
    #     return self.registry.get_transformer(event)
