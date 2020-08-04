"""
Base transformer to transform common event fields.
"""
import uuid
from logging import getLogger

from django.contrib.auth import get_user_model

from student.models import anonymous_id_for_user    # pylint: disable=import-error

from edx_analytics_transformers.transformers.base_transformer import BaseTransformer
from edx_analytics_transformers.transformers.caliper.constants import CALIPER_EVENT_CONTEXT
from edx_analytics_transformers.transformers.caliper.helpers import convert_datetime_to_iso


logger = getLogger()
User = get_user_model()


class CaliperTransformer(BaseTransformer):
    """
    Base transformer class to transform common fields.
    """
    required_fields = (
        'type',
        'object',
        'action'
    )

    def base_transform(self):
        """
        Transform common Caliper fields.
        """
        self._add_generic_fields()
        self._add_actor_info()
        self._add_referrer()

    def _add_generic_fields(self):
        """
        Add all of the generic fields to the transformed_event object.
        """
        self.transformed_event.update({
            '@context': CALIPER_EVENT_CONTEXT,
            'id': uuid.uuid4().urn,
            'eventTime': convert_datetime_to_iso(self.event.get('timestamp'))
        })
        self.transformed_event['object'] = {
            'extensions': {
                'course_id': self.event['context'].get('course_id', '')
            }
        }

    def _add_actor_info(self):
        """
        Add all generic information related to `actor`.
        """
        anonymous_id = self._generate_anonymous_id()

        self.transformed_event['actor'] = {
            'id': anonymous_id,
            'type': 'Person'
        }

    def _generate_anonymous_id(self):
        """
        Generate anonymous user id.

        If no anonymous id is generated, return "anonymous"

        Returns:
            str
        """
        username = self.event['context'].get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.info('User with username "%s" does not exist. '
                        'Cannot generate anonymous ID', username)

            anonymous_id = 'anonymous'
        else:
            anonymous_id = anonymous_id_for_user(user, None)

        return anonymous_id

    def _add_referrer(self):
        """
        Adds information of an Entity that represents the referring context.
        """
        self.transformed_event['referrer'] = {
            'id': self.event['context'].get('referer'),
            'type': 'WebPage'
        }
