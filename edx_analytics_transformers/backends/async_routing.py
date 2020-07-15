"""Route events to processors and backends"""

from __future__ import absolute_import

import json
import logging

import six

from edx_analytics_transformers.backends.routing import RoutingBackend
from edx_analytics_transformers.processors.exceptions import EventEmissionExit
from edx_analytics_transformers.helpers import GenericJSONEncoder
from edx_analytics_transformers.tasks import async_send


LOG = logging.getLogger(__name__)


class AsyncRoutingBackend(RoutingBackend):
    """
    Route events to configured backends asynchronously
    """

    def send(self, event):
        """
        Process the event using all registered processors and send it to all registered backends.
        """
        try:
            processed_event = self.process_event(event)
        except EventEmissionExit:
            return

        try:
            json_event = json.dumps(processed_event, cls=GenericJSONEncoder)
        except ValueError:
            LOG.exception(
                'JSONEncodeError: Unable to encode event:%s', processed_event
            )
            return

        for name, backend in six.iteritems(self.backends):
            try:
                json_backend = json.dumps(backend, cls=GenericJSONEncoder)
            except ValueError:
                LOG.exception(
                    'JSONEncodeError: Unable to encode backend: %s', name
                )
                continue

            async_send.delay(json_backend, json_event, backend_name=name)
