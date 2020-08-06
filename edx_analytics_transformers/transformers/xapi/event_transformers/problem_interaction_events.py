"""
Transformers for problem interaction events.

# TODO: Implement transformer for `edx.problem.completed`.
"""
from django.conf import settings
from django.urls import reverse

from tincan import (
    Activity,
    ActivityDefinition,
    ActivityList,
    LanguageMap,
    InteractionComponent,
    InteractionComponentList,
    Context,
    ContextActivities,
    Verb,
    Extensions,
    Result
)

from edx_analytics_transformers.transformers.caliper.helpers import get_block_id_from_event_referrer
from edx_analytics_transformers.transformers.xapi import constants
from edx_analytics_transformers.transformers.xapi.registry import XApiTransformersRegistry
from edx_analytics_transformers.transformers.xapi.transformer import XApiTransformer

# map open edx problems interation types to xAPI valid interaction types
INTERACTION_TYPES_MAP = {
    'choiceresponse': 'choice',
    'multiplechoiceresponse': 'choice',
    'numericalresponse': 'numeric',
    'stringresponse': 'fill-in',
    'customresponse': 'other',
    'coderesponse': 'performance',  # or "other"?
    'externalresponse': 'performance',  # or "other"?
    'formularesponse': 'fill-in',
    'schematicresponse': 'sequencing',  # or "other"?
    'imageresponse': 'matching',
    'annotationresponse': 'fill-in',
    'choicetextresponse': 'choice',
    'optionresponse': 'choice',
    'symbolicresponse': 'fill-in',
    'truefalseresponse': 'true-false',
}


DEFAULT_INTERACTION_TYPE = 'other'

VERB_MAP = {
    'edx.grades.problem.submitted': {
        'id': constants.XAPI_VERB_ATTEMPTED,
        'display': constants.ATTEMPTED
    },
    'problem_check': {
        'id': constants.XAPI_VERB_ANSWERED,
        'display': constants.ANSWERED
    },
    'showanswer': {
        'id': constants.XAPI_VERB_ASKED,
        'display': constants.ASKED
    },
    'edx.problem.hint.demandhint_displayed': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
    },
}


@XApiTransformersRegistry.register('showanswer')
@XApiTransformersRegistry.register('edx.problem.hint.demandhint_displayed')
class ProblemEventsTransformer(XApiTransformer):
    """
    Transform problem interaction events into xAPI format.
    """
    additional_fields = ('context', )

    def get_verb(self):
        """
        Get verb for xAPI transformed event.

        Returns:
            `Verb`
        """
        event_name = self.event['name']
        return Verb(
            id=VERB_MAP[event_name]['id'],
            display=LanguageMap({constants.EN: VERB_MAP[event_name]['display']})
        )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        # TODO: Add definition[name] of problem once it is added in the event.
        return Activity(
            id=self.find_nested('problem_id') or self.find_nested('module_id'),
            definition=ActivityDefinition(
                # TODO: QUESTION activity for problems other than CAPA
                type=constants.XAPI_ACTIVITY_INTERACTION,
            ),
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """
        return Context(
            # FIXME: registration must be a UUID
            # registration=get_anonymous_user_id_by_username(
            #     self.event['context']['username'],
            #     self.event['context']['course_id']
            # ),
            contextActivities=self.get_context_activities()
        )

    def get_context_activities(self):
        """
        Get context activities for xAPI transformed event.

        Returns:
            `ContextActivities`
        """
        parent_activities = [
            Activity(
                id='{root_url}{course_root_url}'.format(
                    root_url=settings.LMS_ROOT_URL,
                    course_root_url=reverse('course_root', kwargs={
                        'course_id': self.event['context']['course_id']
                    }),
                ),
                object_type=constants.XAPI_ACTIVITY_COURSE
            ),
        ]
        return ContextActivities(
            parent=ActivityList(parent_activities),
        )


@XApiTransformersRegistry.register('edx.grades.problem.submitted')
class ProblemSubmittedTransformer(ProblemEventsTransformer):
    """
    Transform problem interaction related events into xAPI format.
    """
    additional_fields = ('context', 'result')

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        event_data = self.event['data']
        return Result(
            success=event_data['weighted_earned'] >= event_data['weighted_possible'],
            score={
                'min': 0,
                'max': event_data['weighted_possible'],
                'raw': event_data['weighted_earned'],
                'scaled': event_data['weighted_earned']/event_data['weighted_possible']
            }
        )


@XApiTransformersRegistry.register('problem_check')
class ProblemCheckTransformer(ProblemEventsTransformer):
    """
    Transform problem interaction related events into xAPI format.
    """
    additional_fields = ('context', 'result', )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        xapi_object = super(ProblemCheckTransformer, self).get_object()

        # If the event was generated from browser, there is no `problem_id`
        # or `module_id` field. Therefore we get block id from the referrer.
        if self.event['context']['event_source'] == 'browser':
            xapi_object.id = get_block_id_from_event_referrer(self.event) or self.find_nested('referer')
            xapi_object.definition.extensions = Extensions({
                'data': self.event['data']
            })
            return xapi_object

        interaction_type = self._get_interaction_type()
        answers = self._get_answers_list()
        xapi_object.definition.interaction_type = interaction_type
        xapi_object.definition.correct_responses_pattern = answers

        if interaction_type == 'choice':
            xapi_object.definition.choices = self._get_choices_list()

        return xapi_object

    def _get_interaction_type(self):
        """
        Convert the Open edX's events response type into xAPI supported
        interaction type.

        Return "other" if the mapping does not exist for the event.

        Returns:
            str
        """
        response_type = self.find_nested('response_type')
        try:
            return INTERACTION_TYPES_MAP[response_type]
        except KeyError:
            return DEFAULT_INTERACTION_TYPE

    def _get_answers_list(self):
        """
        Get the answers list from the event.

        The event contains answers in the form of:

        {
            ...,
            "data": {
                "answers":{
                    "[id]": <Answer(s)>
                }

            }
        }

        Where these answer(s) can either be a single string, or a list of strings.

        Returns:
            list
        """
        answers = self.find_nested('answers')
        try:
            answers = next(iter(answers.values()))
            if isinstance(answers, str):
                return [answers]

            return answers
        except StopIteration:
            return []

    def _get_choices_list(self):
        """
        Return list of choices for the problem.

        Every choice is an InteractionComponent containing id (obtained from the
        `data[answers][<ID>]` map) and a correspoding display name (obtained from
        `data[submission][<ID>][answer]` map).

        These answer(s) could either be a single string or be a list of strings.

        Returns:
            InteractionComponentList<InteractionComponent>
        """
        answers = self._get_answers_list()
        answers_descriptions = self.find_nested('answer')
        if isinstance(answers_descriptions, str):
            answers_descriptions = [answers_descriptions, ]
        return InteractionComponentList([
            InteractionComponent(
                id=answer,
                description=LanguageMap({constants.EN: description})
            ) for (answer, description) in zip(answers, answers_descriptions)
        ])

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            Result
        """
        # Do not transform result if the event is generated from browser
        if self.event['context']['event_source'] == 'browser':
            return None

        event_data = self.event['data']

        return Result(
            success=event_data['success'] == 'correct',
            score={
                'min': 0,
                'max': event_data['max_grade'],
                'raw': event_data['grade'],
                'scaled': event_data['grade']/event_data['max_grade']
            },
            response=self.find_nested('answers')
        )
