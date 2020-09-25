"""
Processor to add enterprise information for the user.
"""
from logging import getLogger

from django.contrib.auth import get_user_model

# pylint: disable=import-error
from openedx.features.enterprise_support.api import EnterpriseApiClient, enterprise_enabled


logger = getLogger(__name__)
User = get_user_model()


class EnterpriseContextProvider:
    """
    Processor to add enterprise information for the user.
    """

    def __call__(self, event):
        """
        Add enterprise information for the user in current
        event
        """
        if not enterprise_enabled():
            logger.info('Enterprise service is disabled. Cannot add enterprise information')
            return event

        username = event['context'].get('username')

        if not username:
            return event

        try:
            user = User.objects.get(username=username)
            enterprise_learner_data = EnterpriseApiClient(user=user).fetch_enterprise_learner_data(user)
            if enterprise_learner_data['results']:
                event['context']['enterprise_uuid'] = (enterprise_learner_data['results'][0]
                                                       ['enterprise_customer']['uuid'])

        except User.DoesNotExist:
            logger.error('Cannot get enterprise information for non-existent user {}'.format(username))
            return event

        except Exception:   # pylint: disable=broad-except
            logger.exception('Exception occurred while trying to get enterprise information '
                             'for the user {}'.format(username), exc_info=True)
            return event

        return event
