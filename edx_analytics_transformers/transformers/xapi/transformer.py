"""
xAPI Transformer Class
"""
from tincan import Activity, ActivityDefinition, Agent, LanguageMap, Statement, Context

from edx_analytics_transformers.transformers.base_transformer import BaseTransformer
from edx_analytics_transformers.transformers.helpers import get_anonymous_user_id_by_username


class XApiTransformer(BaseTransformer):
    """
    xAPI Transformer Class
    """
    required_fields = (
        'object',
        'verb',
    )

    def transform(self):
        transformed_props = super(XApiTransformer, self).transform()
        # TODO: initialize statement
        return Statement(**transformed_props)

    def base_transform(self):
        self.transformed_event = {
            'actor': self.get_actor(),
            # 'verb': self.get_verb(),
            # 'object': self.get_object(),
            # 'result': self.get_result(),
            'timestamp': self.get_timestamp()
        }

    def get_actor(self):
        return Agent(
            # name=get_anonymous_user_id_by_username(self.event['context'].get('username')),
            openid=get_anonymous_user_id_by_username(self.event['context'].get('username')),
        )

    def get_timestamp(self):
        """
        Get the Timestamp for the statement.
        """
        return self.event['timestamp']
