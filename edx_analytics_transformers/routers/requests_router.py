"""
Generic router to send events to hosts.
"""
import logging

from eventtracking.processors.exceptions import EventEmissionExit

from edx_analytics_transformers.utils.http_client import HttpClient
from edx_analytics_transformers.django.models import RouterConfiguration


logger = logging.getLogger(__name__)


ROUTER_STRATEGY_MAPPING = {
    'AUTH_HEADERS': HttpClient,
}


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

        router = RouterConfiguration.get_latest_enabled_router(self.backend_name)

        if not router:
            logger.info('Could not find an enabled router configurations for backend %s', self.backend_name)
            return

        hosts = router.get_allowed_hosts(original_event)
        if not hosts:
            logger.info(
                'Event %s is not allowed to be sent to any host for router with backend "%s"',
                original_event['name'], self.backend_name
            )
            return

        for host in hosts:
            updated_event = self.overwrite_event_data(processed_event, host)

            self.dispatch_event(
                original_event['name'],
                updated_event,
                host['router_type'],
                host['host_configurations']
            )

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

    def overwrite_event_data(self, event, host):
        """
        Overwrite/Add values in the event.

        If there is `override_args` key in the host configurations,
        add those keys to the event and overwrite the existing values (if any).

        Arguments:
            event (dict):   Event in which values are to be added/overwritten
            host (dict):    Host configurations dict.

        Returns:
            dict
        """
        if 'override_args' in host:
            event = event.copy()
            event.update(host['override_args'])
            logger.info('Overwriting event with values %s', host['override_args'])
        return event

    def dispatch_event(self, event_name, event, router_type, host_config):
        """
        Send event to configured host.

        Arguments:
            event_name (str)    : name of the original event
            event (dict)        : event dictionary to be delivered.
            router_type (str)   : decides the client to use for sending the event
            host_config (dict)  : contains configurations for the host.
        """
        logger.info(
            'Routing event "%s" for router type "%s"',
            event_name,
            router_type
        )

        try:
            client_class = ROUTER_STRATEGY_MAPPING[router_type]
        except KeyError:
            logger.error('Unsupported routing strategy detected: %s', router_type)
            return

        try:
            client = client_class(**host_config)
            client.send(event)
            logger.info(
                'Successfully dispatched event "%s" using client strategy "%s"',
                event_name,
                router_type
            )

        except Exception:   # pylint: disable=broad-except
            logger.exception(
                'Exception occured while trying to dispatch event "%s"',
                event_name,
                exc_info=True
            )
