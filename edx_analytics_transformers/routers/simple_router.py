import logging
import requests

from eventtracking.processors.exceptions import EventEmissionExit
from edx_analytics_transformers.django.models import RouterConfigFilter


logger = logging.getLogger(__name__)


def get_value_from_dotted_path(dict_obj, dotted_key):
    nested_keys = dotted_key.split('.')
    result = dict_obj
    try:
        for key in nested_keys:
            result = result[key]
    except KeyError:
        return None
    return result


class SimpleRouter:
    def __init__(self, processors=None, host_config=None, backend_name=None):
        self.processors = processors if processors else []
        self.host_config = host_config if host_config else {}
        self.backend_name = backend_name

    def send(self, original_event, transformed_event):
        try:
            logger.info('Processing event %s for router with backend %s', original_event['name'], self.backend_name)
            processed_event = self.process_event(transformed_event)
        except EventEmissionExit:
            return

        logger.info('Successfully processed event %s for router with backend %s',
                    original_event['name'], self.backend_name)

        routers = self.get_configurations()
        for router in routers:
            should_send_event = self.match_with_router_configurations(
                router.configurations,
                original_event,
                transformed_event
            )

            if should_send_event:
                logger.info('event %s allowed to be routed by router %s', original_event['name'], self)
                self.send_event(processed_event, router.configurations['configurations'])
                logger.info('event %s successfully routed by router %s', original_event['name'], self)
            else:
                logger.info('event %s is not allowed to be routed by router %s', original_event['name'], self)
                return

    def match_with_router_configurations(self, router_config, original_event, _):
        match_params = router_config['match']
        for key, value in match_params.items():
            actual_value = get_value_from_dotted_path(original_event, key)
            if not actual_value or (actual_value and actual_value != value):
                return False
        return True

    def get_configurations(self):
        configurations = RouterConfigFilter.get_enabled_routers(self.backend_name)
        return configurations

    def send_event(self, event, router_config):

        logger.info('ROUTER sending event to %s', router_config)
        requests.post(
            router_config['url'],
            json=event,
            headers=router_config.get('headers', {})
        )

        logger.info('ROUTER event sent successfully')

    def process_event(self, event):
        logger.info('Processing event')
        event = event.copy()
        for processor in self.processors:
            event = processor(event)

        return event
