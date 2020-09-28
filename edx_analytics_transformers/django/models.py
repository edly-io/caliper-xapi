"""
Models for filtering of events
"""
import logging

from config_models.models import ConfigurationModel
from django.db import models

from edx_analytics_transformers.utils.fields import EncryptedJSONField


logger = logging.getLogger(__name__)


ROUTER_CACHE_NAMESPACE = 'edx_analytics.request_router'


def get_value_from_dotted_path(dict_obj, dotted_key):
    """
    Map the dotted key to nested keys for dict and return the matching value.

    For example:
        'key_a.key_b.key_c' will look for the folowing value:

        {
            'key_a': {
                'key_b': {
                    'key_c': 'final value'
                }
            }
        }

    Arguments:
        dict_obj (dict)  :    dictionary for which the value is required
        dotted_key (str) :    dotted key string for the dict

    Returns:
        ANY :                 depends upon the value in dict
    """
    nested_keys = dotted_key.split('.')
    result = dict_obj
    try:
        for key in nested_keys:
            result = result[key]
    except KeyError:
        return None
    return result


# .. toggle_description: Configuration models defined for backend_name and enterprise_uuid combinations.
# will be used for system-wide events if no enterprise_uuid is set.
# .. toggle_implementation: ConfigurationModel
class RouterConfiguration(ConfigurationModel):
    """
    Configurations for filtering and then routing events to hosts.
    """
    KEY_FIELDS = ('backend_name', 'enterprise_uuid')
    backend_name = models.CharField(
        max_length=50,
        verbose_name='Backend name',
        null=False,
        blank=False,
        help_text=(
            'Name of the tracking backend on which this router should be applied.'
            '<br/>'
            'Please note that this field is <b>case sensitive.</b>'
        )
    )
    enterprise_uuid = models.UUIDField(
        verbose_name='Enterprise UUID',
        null=True,
        blank=True,
    )

    configurations = EncryptedJSONField()

    class Meta:
        verbose_name = 'Router Configuration'
        verbose_name_plural = 'Router Configurations'

    def __str__(self):
        return '{id} - {backend} - {enabled}'.format(
            id=self.pk,
            backend=self.backend_name,
            enabled='Enabled' if self.enabled else 'Disabled'
        )

    @classmethod
    def get_enabled_router(cls, backend_name, enterprise_uuid=None):
        """
        Return the enabled router for the backend matching the `backend_name` and
        optionally matching the `enterprise_uuid`.

        Arguments:
            backend_name (str):     Name of the backend for which the router is required.
            enterprise_uuid (str):  enterprise UUID for which the router is required.

        Returns:
            RouterConfiguration or None
        """
        router_config = cls.current(backend_name, enterprise_uuid)
        return router_config if router_config.enabled else None

    def get_allowed_hosts(self, original_event):
        """
        Returns list of hosts to which the `transformed_event` is allowed to be sent.

        Arguments:
            original_event    (dict):       original event dict

        Returns
            list<dict>
        """
        allowed_hosts = []
        for host_config in self.configurations:
            is_allowed = self._match_event_for_host(original_event, host_config)

            if is_allowed:
                allowed_hosts.append(host_config)

        return allowed_hosts

    def _match_event_for_host(self, original_event, host_config):
        """
        Return True if the `original_event` matches the `match_params` in `host_config`.

        Arguments:
            original_event    (dict):     original event dict
            host_config       (dict):     host configurations dict

        Returns:
            bool
        """
        for key, value in host_config['match_params'].items():
            if get_value_from_dotted_path(original_event, key) != value:
                return False
        return True
