"""
Registry to keep track of event transforems
"""
from edx_analytics_transformers.transformers.caliper.exceptions import NoTransformerImplemented


class TransformerRegistry:
    """
    Registry to keep track of event transforems.
    """

    mapping = {}

    @classmethod
    def register(cls, event_key):
        """
        Decorator to register a transformer for an event

        Arguments:
            event_key (str):    unique event identifier string.
        """
        def __inner__(transformer):
            """
            Register transformer for a given event.

            Arguments:
                transformer (class):    transformer class for one or more events.
            """
            # TODO: check for existing transformer
            cls.mapping[event_key] = transformer
            return transformer

        return __inner__

    @classmethod
    def get_transformer(cls, event):
        """
        Return an initialized transformer instance for provided `event`.

        Arguements:
            event (dict):   event to be transformed

        Returns:
            Transformer object

        Raises:
            `NoTransformerImplemented`:  if matching transformer is not found.
        """
        event_name = event.get('name')
        try:
            return cls.mapping[event_name](event)
        except KeyError:
            raise NoTransformerImplemented
