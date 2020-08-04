"""
Test the transformers for all of the currently supported events
"""
import json
import os

import ddt
from mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from edx_analytics_transformers.django.tests.factories import UserFactory
from edx_analytics_transformers.transformers.caliper.registry import CaliperTransformersRegistry
from edx_analytics_transformers.transformers.xapi.registry import XApiTransformersRegistry


User = get_user_model()

TEST_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

EVENT_FIXTURE_FILENAMES = [
    event_file_name for event_file_name in os.listdir(
        '{}/fixtures/current/'.format(TEST_DIR_PATH)
    ) if event_file_name.endswith(".json")
]


def mocked_course_reverse(_, kwargs):
    """
    Return the reverse method to return course root URL.
    """
    return '/courses/{}'.format(kwargs.get('course_id'))


class BaseTestTransformers(TestCase):
    """
    Base tests class for Transformers test cases.
    """
    # no limit to diff in the output of tests
    maxDiff = None

    def setUp(self):
        super(BaseTestTransformers, self).setUp()
        UserFactory.create(username='edx')


class TransformersTestsMixin:
    """
    Abstract tests class for Transformers test cases.
    """
    registry = None
    standard = None
    tolerate_fields = ()
    required_keys = ()

    @patch('edx_analytics_transformers.transformers.caliper.event_transformers.enrollment_events.reverse',
           side_effect=mocked_course_reverse)
    def test_event_transformer(self, *_):
        supported_events = [
            event_file_name for event_file_name in os.listdir(
                '{}/fixtures/{}/'.format(TEST_DIR_PATH, self.standard)
            ) if event_file_name.endswith(".json")
        ]
        for event in supported_events:
            with self.subTest('Test transforming event {} into {} format.'.format(
                event, self.standard
            ), event=event):
                self.assert_transformation(event)

    def assert_transformation(self, event_filename):
        """
        Assert that the event is transformed correctly.

        Arguments:
            event_filename (str) :  name of the file containing the event
        """
        input_event_file_path = '{test_dir}/fixtures/current/{event_filename}'.format(
            test_dir=TEST_DIR_PATH, event_filename=event_filename
        )

        expected_event_file_path = '{test_dir}/fixtures/{standard}/{event_filename}'.format(
            test_dir=TEST_DIR_PATH,
            standard=self.standard,
            event_filename=event_filename
        )

        with open(input_event_file_path) as current, open(expected_event_file_path) as expected:
            original_event = json.loads(current.read())
            expected_event = json.loads(expected.read())

            # actual_transformed_event = transform_event(original_event)
            actual_transformed_event = self.get_transformed_event(original_event)

            # id is a randomly generated UUID therefore not comparing that
            self.assert_required_keys(actual_transformed_event)
            self.remove_tolerated_fields(expected_event, actual_transformed_event)

            self.assertDictEqual(expected_event, actual_transformed_event)

    def get_transformed_event(self, original_event):
        """
        Transform the original event using the configured registry.

        Making this separate method so that inheriting classes can override
        this method to convert their transformed events into JSON forms
        so that they could be compared with the expected event JSON.

        Arguments:
            original_event (dict) :     original event from edX

        Returns:
            dict
        """
        return self.registry.get_transformer(original_event).transform()

    def assert_required_keys(self, transformed_event):
        """
        Asserts that the required keys exist in transformed event
        irrespective of their value.

        Usually such keys have randomly generated values like UUID.

        Arguments:
            transfromed_event (dict) :  actual transformed event

        Raises:
            AssertionError
        """
        for key in self.required_keys:
            self.assertIn(key, transformed_event)

    def remove_tolerated_fields(self, expected_event, transformed_event):
        """
        Remove the fields that are tolerated while comparing the
        transformed events.

        Arguments:
            expected_event (dict) :     expected event from fixture
            transfromed_event (dict) :  actual transformed event
        """
        for key in self.tolerate_fields:
            if key in expected_event:
                expected_event.pop(key)
            if key in transformed_event:
                transformed_event.pop(key)


@ddt.ddt
class TestCaliperTransformers(BaseTestTransformers, TransformersTestsMixin):
    """
    Test that supported events are transformed correctly.
    """
    registry = CaliperTransformersRegistry
    standard = 'caliper'
    required_keys = ('id',)
    tolerate_fields = ('id',)


@ddt.ddt
class TestXApiTransformers(BaseTestTransformers, TransformersTestsMixin):
    """
    Test that supported events are transformed correctly.
    """
    registry = XApiTransformersRegistry
    standard = 'xapi'

    def get_transformed_event(self, original_event):
        """
        Transform the original event using the configured registry.

        Making this separate method so that inheriting classes can override
        this method to convert their transformed events into JSON forms
        so that they could be compared with the expected event JSON.

        Arguments:
            original_event (dict) :     original event from edX

        Returns:
            dict
        """
        transformed = self.registry.get_transformer(original_event).transform()
        return json.loads(transformed.to_json())
