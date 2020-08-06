"""
xAPI Transformer Class
"""
from tincan import Agent, Statement, LanguageMap, Verb

from edx_analytics_transformers.transformers.base_transformer import BaseTransformer
from edx_analytics_transformers.transformers.helpers import get_anonymous_user_id_by_username
from edx_analytics_transformers.transformers.xapi import constants


class XApiTransformer(BaseTransformer):
    """
    xAPI Transformer Class
    """
    required_fields = (
        'object',
        'verb',
    )

    def transform(self):
        """
        Return transformed `Statement` object.

        `BaseTransformer`'s `transform` method will return dict containing
        xAPI objects in transformed fields. Here we return a `Statement` object
        constructed using those fields.

        Returns:
            `Statement`
        """
        transformed_props = super(XApiTransformer, self).transform()
        return Statement(**transformed_props)

    def base_transform(self):
        """
        Transform the fields that are common for all events.
        """
        # TODO: Move context registration in base transform
        self.transformed_event = {
            'actor': self.get_actor(),
            'timestamp': self.get_timestamp()
        }

    def get_actor(self):
        """
        Return `Agent` object for the event.

        Returns:
            `Agent`
        """
        return Agent(
            # name=get_anonymous_user_id_by_username(self.event['context'].get('username')),
            openid=get_anonymous_user_id_by_username(self.event['context'].get('username')),
        )

    def get_timestamp(self):
        """
        Get the Timestamp for the statement.

        Returns:
            str
        """
        return self.event['timestamp']


class XApiVerbTransformerMixin:
    """
    Return transformed Verb object using a predefined `verb_map`
    in the transformer.

    The `verb_map` dictionary must contain `id` and `display` (language "en")
    for each verb value.

    This is helpful in base transformer class which are going to be
    transforming multiple transformers.
    """
    verb_map = None

    def get_verb(self):
        """
        Get verb for xAPI transformed event.

        Returns:
            `Verb`
        """
        event_name = self.event['name']

        verb = self.verb_map[event_name]

        return Verb(
            id=verb['id'],
            display=LanguageMap({constants.EN: verb['display']})
        )
