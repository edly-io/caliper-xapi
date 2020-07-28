"""
Base transformer to add or transform common data values.
"""
import json
from logging import getLogger

import six


logger = getLogger(__name__)


class BaseTransformer:
    """
    Base transformer class.

    Other transformers are inherited from this class.
    """
    required_fields = ()
    additional_fields = ()

    def __init__(self, event):
        """
        Initialize the transformer with the event to be transformed.

        Arguments:
            event (dict):   event to be transformed
        """
        self.event = event.copy()
        self.transformed_event = {}

    def json_load_event(self):
        """
        Update the current event's `data` value with JSON decoded dict if its a string.
        """
        if isinstance(self.event['data'], six.string_types):
            self.event['data'] = json.loads(self.event['data'])

    def transform(self):
        """
        Transform the edX event.

        Returns:
            dict
        """
        transforming_fields = self.required_fields + self.additional_fields
        for key in transforming_fields:
            if hasattr(self, key):
                value = getattr(self, key)
                self.transformed_event[key] = value
            elif hasattr(self, 'get_{}'.format(key)):
                value = getattr(self, 'get_{}'.format(key))(self.event, self.transformed_event)
                self.transformed_event[key] = value
            else:
                raise ValueError(
                    'Cannot find value for "{}" in transforomer {} for the event "{}"'.format(
                        key, self.__class__.__name__, self.event['name']
                    )
                )

        return self.transformed_event
