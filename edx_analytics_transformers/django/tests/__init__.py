"""
Execute the tasks required before running the tests.
"""

import sys

import mock

FROZEN_UUID = '44701a8e-7be7-4f55-a254-e2f70275ae2a'


def _mock_third_party_modules():
    """
    Mock third party modules used in the app.
    """
    student_module = mock.MagicMock()
    student_module.anonymous_id_for_user.return_value = 'anonymous_id'
    sys.modules['student.models'] = student_module

    mocked_enterprise = mock.MagicMock()
    mocked_enterprise.EnterpriseApiClient.fetch_enterprise_learner_data.return_value = {
        'results': [
            {
                'enterprise_customer': {
                    'uuid': FROZEN_UUID
                }
            }
        ]
    }
    mocked_enterprise.EnterpriseApiClient.enterprise_enabled.return_value = True
    sys.modules['openedx.features.enterprise_support.api'] = mocked_enterprise


_mock_third_party_modules()
