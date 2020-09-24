"""
Models for filtering of events
"""
import logging

from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords

from edx_django_utils.cache import TieredCache, get_cache_key
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


class RouterConfiguration(models.Model):
    """
    Configurations for filtering and then routing events to hosts.
    """

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
    is_enabled = models.BooleanField(
        default=True,
        verbose_name='Is Enabled'
    )
    configurations = EncryptedJSONField()
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Router Configurations'
        verbose_name_plural = 'Router Configurations'
        ordering = ('backend_name', 'is_enabled')
        unique_together = (('backend_name', 'enterprise_uuid'), )

    def clean(self):
        """
        Make sure that unique together constraint is applied to fields even
        if they have `None` stored in them.

        Django's default `unique_together` doesn't work if the fields are nullable.
        """
        existing = RouterConfiguration.objects.filter(
            backend_name=self.backend_name,
            enterprise_uuid=self.enterprise_uuid
        )

        # Since we are using `HistoricalRecords` for managing the history,
        # everytime the configuration is updated, a new object is created.
        # We need to check that all existing configurations have same ID as the
        # current one (that means the existing objects are just history records
        # of the same configuration).
        for config in existing:
            if config.id != self.id:
                raise ValidationError('Configuration with matching enterprise_uuid '
                                      'and backend_name already exists')

    def __str__(self):
        return '{id} - {backend} - {is_enabled}'.format(
            id=self.pk,
            backend=self.backend_name,
            is_enabled='Enabled' if self.is_enabled else 'Disabled'
        )

    @classmethod
    def get_enabled_router(cls, backend_name, enterprise_uuid=None):
        """
        Return the enabled router for the backend matching the `backend_name` and
        optionally matching the `enterprise_uuid`.

        First look for the router in the cache and return its value from there if found.
        If not found in the cache, call the `_get_enabled_router` method to get the
        router and store it in the cache before returning it.

        Arguments:
            backend_name (str):     Name of the backend for which the router is required.
            enterprise_uuid (str):  enterprise UUID for which the router is required.

        Returns:
            RouterConfiguration or None
        """
        router_cache_key = get_cache_key(
            namespace=ROUTER_CACHE_NAMESPACE,
            backend_name=backend_name,
            enterprise_uuid=enterprise_uuid
        )

        cache_response = TieredCache.get_cached_response(router_cache_key)

        if cache_response.is_found:
            logger.debug(
                'Router is found in cache for backend "%s" and enterprise "%s"',
                backend_name,
                enterprise_uuid
            )
            router = cache_response.value
        else:
            logger.debug(
                'No router was found in cache for backend "%s" and enterprise "%s"',
                backend_name,
                enterprise_uuid
            )

            router = cls._get_enabled_router(backend_name=backend_name, enterprise_uuid=enterprise_uuid)

            TieredCache.set_all_tiers(router_cache_key, router)
            logger.debug(
                'Router has been stored in cache for backend "%s" and enterprise "%s"',
                backend_name,
                enterprise_uuid
            )

        return router

    @classmethod
    def _get_enabled_router(cls, backend_name, enterprise_uuid=None):
        """
        Return the enabled router for the backend matching the `backend_name` and
        optionally matching the `enterprise_uuid`.

        Return `None` if there is no filter matching the criteria.

        Arguments:
            backend_name (str):    Name of the backend for which the filter is required.
            enterprise_uuid (str):  enterprise UUID for which the router is required.

        Returns:
            RouterConfiguration or None
        """
        try:
            return cls.objects.get(
                is_enabled=True,
                backend_name=backend_name,
                enterprise_uuid=enterprise_uuid
            ).history.most_recent()
        except cls.DoesNotExist:
            return None

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
