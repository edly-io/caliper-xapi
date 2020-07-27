"""
Transformers for problem interaction events.
"""
from edx_analytics_transformers.transformers.caliper.helpers import get_block_id_from_event_referrer

from edx_analytics_transformers.transformers.caliper.base_transformer import CaliperTransformer
from edx_analytics_transformers.transformers.caliper.registry import TransformerRegistry


EVENT_ACTION_MAP = {
    'problem_check': 'Submitted',
    'edx.grades.problem.submitted': 'Submitted',
    'showanswer': 'Viewed',
    'problem_show': 'Viewed',
    'edx.problem.hint.demandhint_displayed': 'Viewed',
    'edx.problem.completed': 'Completed'
}

OBJECT_TYPE_MAP = {
    'problem_check': 'Assessment',
    'edx.grades.problem.submitted': 'Assessment',
    'showanswer': 'Frame',
    'problem_show': 'Frame',
    'edx.problem.hint.demandhint_displayed': 'Frame',
    'edx.problem.completed': 'AssessmentItem'
}

EVENT_TYPE_MAP = {
    'problem_check': 'AssessmentEvent',
    'edx.grades.problem.submitted': 'AssessmentEvent',
    'showanswer': 'ViewEvent',
    'problem_show': 'ViewEvent',
    'edx.problem.hint.demandhint_displayed': 'ViewEvent',
    'edx.problem.completed': 'AssessmentItemEvent'
}


@TransformerRegistry.register('problem_check')
@TransformerRegistry.register('edx.grades.problem.submitted')
@TransformerRegistry.register('showanswer')
@TransformerRegistry.register('edx.problem.hint.demandhint_displayed')
@TransformerRegistry.register('edx.problem.completed')
class ProblemEventsTransformers(CaliperTransformer):
    """
    Transform problem interaction related events into caliper format.
    This transformer can transform the following events:

    Currently there is no "edx.problem.completed" event in open edx but
    will be added in future as per the mapping document:
    https://docs.google.com/spreadsheets/u/1/d/1z_1IGFVDF-wZToKS2EGXFR3s0NXoh6tTKhEtDkevFEM/edit?usp=sharing.
    """

    def get_type(self, current_event, _):
        """
        Return type for caliper event.

        Arguments:
            current_event (dict):   untransformed event
            _             (dict):   transformed event

        Returns:
            str
        """
        return EVENT_TYPE_MAP[current_event['name']]

    def get_action(self, current_event, _):
        """
        Return action for caliper event.

        Arguments:
            current_event (dict):   untransformed event
            _             (dict):   transformed event

        Returns:
            str
        """
        return EVENT_ACTION_MAP[current_event['name']]

    def get_object(self, current_event, transformed_event):
        """
        Return transformed object for caliper event.

        Arguments:
            current_event     (dict):   untransformed event
            transformed_event (dict):   transformed event

        Returns:
            dict
        """
        if 'problem_id' in current_event['data']:
            object_id = current_event['data']['problem_id']
        elif 'module_id' in current_event['data']:
            object_id = current_event['data']['module_id']
        else:
            object_id = get_block_id_from_event_referrer(current_event) or current_event['context']['referer']

        caliper_object = transformed_event['object']
        caliper_object.update({
            'id': object_id,
            'type': OBJECT_TYPE_MAP[current_event['name']],
        })

        if current_event['context'].get('event_source') == 'browser':
            caliper_object['extensions'].update({
                'data': current_event['data']
            })
        else:
            caliper_object['extensions'].update(current_event['data'])
            # problem_id is already being used as object id
            if 'problem_id' in caliper_object['extensions']:
                del caliper_object['extensions']['problem_id']

        if 'user_id' in caliper_object['extensions']:
            del caliper_object['extensions']['user_id']

        return caliper_object
