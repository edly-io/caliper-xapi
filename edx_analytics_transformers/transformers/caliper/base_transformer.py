"""
Base transformer to add or transform common data values.
"""
import json
import uuid
from logging import getLogger

import six
from django.contrib.auth import get_user_model

from student.models import anonymous_id_for_user    # pylint: disable=import-error

from edx_analytics_transformers.transformers.caliper.helpers import convert_datetime


CALIPER_EVENT_CONTEXT = 'http://purl.imsglobal.org/ctx/caliper/v1p1'

logger = getLogger()
User = get_user_model()


class CaliperTransformer:
    """
    Base transformer class to transform common fields.

    Other transformers are inherited from this class.
    """
    transforming_fields = (
        'type',
        'object',
        'action'
    )

    def __init__(self, event):
        """
        Initialize the transformer with the event to be transformed.

        Arguments:
            event (dict):   event to be transformed
        """
        self.event = event.copy()

    def json_load_event(self):
        """
        Update the current event's `data` value with JSON decoded dict if its a string.
        """
        if isinstance(self.event['data'], six.string_types):
            self.event['data'] = json.loads(self.event['data'])

    def transform(self):
        """
        Transform the edX event into Caliper event.

        Returns:
            dict
        """
        transformed_event = {}
        self._base_transform(transformed_event)

        for key in self.transforming_fields:
            if hasattr(self, key):
                value = getattr(self, key)
                transformed_event[key] = value
            elif hasattr(self, 'get_{}'.format(key)):
                value = getattr(self, 'get_{}'.format(key))(self.event, transformed_event)
                transformed_event[key] = value
            else:
                raise ValueError(
                    'Cannot find value for "{}" in transforomer {} for the event "{}"'.format(
                        key, self.__class__.__name__, self.event['name']
                    )
                )

        return transformed_event

    def _base_transform(self, transformed_event):
        """
        Transform common Caliper fields.

        Arguments:
            transformed_event (dict)   : partially transformed event
        """
        self._add_generic_fields(transformed_event)
        self._add_actor_info(transformed_event)
        self._add_referrer(transformed_event)

    def _add_generic_fields(self, transformed_event):
        """
        Add all of the generic fields to the transformed_event object.

        Arguments:
            transformed_event (dict)   : partially transformed event
        """
        transformed_event.update({
            '@context': CALIPER_EVENT_CONTEXT,
            'id': uuid.uuid4().urn,
            'eventTime': convert_datetime(self.event.get('timestamp'))
        })
        transformed_event['object'] = {
            'extensions': {
                'course_id': self.event['context'].get('course_id', '')
            }
        }

    def _add_actor_info(self, transformed_event):
        """
        Add all generic information related to `actor`.

        Arguments:
            transformed_event (dict)   : partially transformed event
        """
        anonymous_id = self._generate_anonymous_id()

        transformed_event['actor'] = {
            'id': anonymous_id,
            'type': 'Person'
        }

    def _generate_anonymous_id(self):
        """
        Generate anonymous user id using the username and course_id
        in the event data. If no anonymous id is generated, return "anonymous"

        Returns:
            str
        """
        # Prefer None over empty course_id
        course_id = self.event['context'].get('course_id') or None
        username = self.event['context'].get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error('User with username "%s" does not exist. '
                         'Cannot generate anonymous ID', username)

            anonymous_id = 'anonymous'
        else:
            anonymous_id = anonymous_id_for_user(user, course_id)

        return anonymous_id

    def _add_referrer(self, transformed_event):
        """
        Adds information of an Entity that represents the referring context.

        Arguments:
            transformed_event (dict)   : partially transformed event
        """
        transformed_event['referrer'] = {
            'id': self.event['context'].get('referer'),
            'type': 'WebPage'
        }
