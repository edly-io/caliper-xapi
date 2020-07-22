"""
Registry to keep track of event transforems
"""
from edx_analytics_transformers.transformers.caliper.exceptions import NoTransformerImplemented


class TransformerRegistry:
    """
    This class keeps tracks of event to transformer mapping.
    """

    mapping = {}

    @classmethod
    def register(cls, event_key):
        """
        Decorator to register a transformer for an event
        """
        def __inner__(transformer):
            # TODO: check for existing transformer
            cls.mapping[event_key] = transformer
            return transformer

        return __inner__

    @classmethod
    def get_transformer(cls, event):
        """
        Get transformer class for an event and return initialized
        transformer instance.

        Raise "NoTransformerImplemented" if matching transformer is not found.
        """
        event_name = event.get('name')
        try:
            return cls.mapping[event_name](event)
        except KeyError:
            raise NoTransformerImplemented
