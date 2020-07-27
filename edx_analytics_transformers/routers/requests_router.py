"""
Generic router to send events to hosts.
"""
import logging
import requests

from eventtracking.processors.exceptions import EventEmissionExit
from edx_analytics_transformers.django.models import RouterConfigFilter


logger = logging.getLogger(__name__)


class RequestsRouter:
    """
    Router to send events to hosts using requests library.
    """

    def __init__(self, processors=None, backend_name=None):
        """
        Initialize the router.

        Arguments:
            processors (list):   list of processor instances
            backend_name (str):  name of the router backend
        """
        self.processors = processors if processors else []
        self.backend_name = backend_name

    def send(self, original_event, transformed_event):
        """
        Send the event to configured routers after processing it.

        Event is processed through the configured processors. A router config
        object matching the backend_name (and that was modified last) is used
        to get the list of hosts to which the event is required to be delivered to.
        `requests` module is then used to send the event to such hosts.

        Arguments:
            original_event (dict):      original event dictionary
            transformed_event (dict):   transformed event dictionary
        """
        try:
            logger.info(
                'Processing event %s for router with backend %s',
                original_event['name'],
                self.backend_name
            )
            processed_event = self.process_event(transformed_event)
        except EventEmissionExit:
            logger.info(
                'Could not process event %s for backend %s\'s router',
                original_event['name'],
                self.backend_name,
                exc_info=True
            )
            return

        logger.info('Successfully processed event %s for router with backend %s',
                    original_event['name'], self.backend_name)

        router = RouterConfigFilter.get_latest_enabled_router(self.backend_name)
        if not router:
            logger.info('Could not find an enabled router configurations for backend %s', self.backend_name)
            return

        hosts = router.get_allowed_hosts(original_event, processed_event)
        if not hosts:
            logger.info(
                'Event %s is not allowed to be sent to any host for router with backend "%s"',
                original_event['name'], self.backend_name
            )
            return

        for host in hosts:
            try:
                requests.post(
                    host['host_configurations']['url'],
                    json=processed_event,
                    headers=host['host_configurations'].get('headers', {})
                )

                logger.info('Event %s is sent successfully to %s.',
                            original_event['name'],
                            host['host_configurations']['url'])

            except Exception:   # pylint: disable=broad-except
                logger.error('Failed to send event %s to %s.', exc_info=True)

    def process_event(self, event):
        """
        Process the event through this router's processors.

        Arguments:
            event (dict):      Event to be processed

        Returns
            dict
        """
        event = event.copy()
        for processor in self.processors:
            event = processor(event)

        return event
