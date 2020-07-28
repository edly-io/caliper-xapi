"""
Transformers for navigation related events.
"""
from edx_analytics_transformers.transformers.caliper.transformer import CaliperTransformer
from edx_analytics_transformers.transformers.caliper.registry import CaliperTransformersRegistry


@CaliperTransformersRegistry.register('edx.ui.lms.sequence.next_selected')
@CaliperTransformersRegistry.register('edx.ui.lms.sequence.previous_selected')
@CaliperTransformersRegistry.register('edx.ui.lms.sequence.tab_selected')
@CaliperTransformersRegistry.register('edx.ui.lms.link_clicked')
@CaliperTransformersRegistry.register('edx.ui.lms.sequence.outline.selected')
@CaliperTransformersRegistry.register('edx.ui.lms.outline.selected')
class NavigationEventsTransformers(CaliperTransformer):
    """
    These events are generated when the user navigates through
    the units in a course.

    "edx.ui.lms.sequence.outline.selected" and "edx.ui.lms.outline.selected" are
    actually same events.
    """
    action = 'NavigatedTo'
    type = 'NavigationEvent'

    def get_object(self, current_event, caliper_event):
        """
        Return transformed object for caliper event.

        Arguments:
            current_event (dict):   untransformed event
            caliper_event (dict):   transformed event

        Returns:
            dict
        """
        caliper_object = caliper_event['object']
        data = current_event['data']

        object_id = data.pop('target_url') if current_event['name'] == 'edx.ui.lms.link_clicked' else data.pop('id')

        caliper_object.update({
            'id': object_id,
            'type': 'WebPage',
            'extensions': data
        })

        return caliper_object
