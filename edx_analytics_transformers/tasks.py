"""
Celery tasks
"""

import json

from celery.utils.log import get_task_logger
from celery import task

from edx_analytics_transformers.django.models import RegExFilter
from edx_analytics_transformers.helpers import BackendJSONDecoder

logger = get_task_logger(__name__)


@task(name='edx_analytics_transformers.tasks.async_send')
def async_send(json_backend, json_event, backend_name):
    """
    Task to load provided json backend, then filter the event using the RegEx filter
    configured for the provided backend.
    If the event is allowed to be processed by the filter, call the backend's send to
    process event asynchronously.

    :param json_backend:    JSON encoded backend
    :param json_event:      JSON encoded event
    :param backend_name:    backend name
    """

    event = json.loads(json_event)
    event_name = event.get('name')

    try:
        backend = json.loads(json_backend, cls=BackendJSONDecoder)
    except ValueError:
        logger.exception(
            'JSONDecodeError: Unable to decode backend: %s.', json_backend
        )
        return

    regex_filter = RegExFilter.get_latest_enabled_filter(backend_name=backend_name)

    if not regex_filter:
        logger.warning('Regular Expression Filter does not have any enabled '
                       'configurations for backend "%s". Allowing the event "%s" to pass through.',
                       backend_name, event_name)

    elif not regex_filter.string_passes_test(event_name):
        logger.info(
            'Event "%s" is not allowed to be processed by backend "%s"',
            event_name, backend_name
        )
        return

    else:
        logger.info(
            'Event "%s" is allowed to be processed by backend "%s"',
            event_name, backend_name
        )

    backend.send(event)
