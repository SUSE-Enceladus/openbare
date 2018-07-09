from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from library.models import (
    AmazonDemoAccount,
    AWSInstance,
    AWSResource,
    Resource
)


class ResourceTestCase(TestCase):
    """Test resource models in library app."""

    @patch('library.models.AmazonAccountUtils')
    def setUp(self, mock_aws_account_utils):
        self.user = User.objects.create_user(
            username='John',
            email='user1@openbare.com',
            password='str0ngpa$$w0rd'
        )
        self.aws_account = AmazonDemoAccount(user=self.user)
        self.aws_account.checkout()
        self.aws_account.save()

    def test_aws_instance(self):
        # Create instance
        detail = {
            'awsRegion': 'us-west-1',
            'responseElements': {
                'instancesSet': {
                    'items': [{'instanceId': 'i-00000000000000000'}]
                }
            }
        }
        event = {
            'EventTime': '2018-06-27T17:10:11Z',
            'EventName': 'RunInstances'
        }

        result = AWSInstance.parse_event(detail, event, self.aws_account)

        self.assertEqual(result, 'i-00000000000000000')

        resources = Resource.objects.all()
        self.assertEqual(len(resources), 1)

        instance = resources[0]
        self.assertEqual(instance.resource_id, 'i-00000000000000000')
        self.assertEqual(instance.scope, 'us-west-1')
        self.assertEqual(instance.lendable_id, 1)
        self.assertEqual(instance.released, None)
        self.assertEqual(instance.preserve, None)
        self.assertNotEqual(instance.acquired, None)

        # Create preserve tag
        detail = {
            'awsRegion': 'us-west-1',
            'requestParameters': {
                'resourcesSet': {
                    'items': [{'resourceId': 'i-00000000000000000'}]
                },
                'tagSet': {
                    'items': [
                        {
                            'key': 'preserve',
                            'value': '2018/10/03'
                        }
                    ]
                }
            },
            'responseElements': {
                '_return': True
            }
        }
        event = {
            'EventTime': '2018-06-27T17:10:12Z',
            'EventName': 'CreateTags'
        }

        AWSResource.parse_event(detail, event, self.aws_account)
        instance = Resource.objects.get(pk=1)
        self.assertNotEqual(instance.preserve, None)

        # Delete preserve tag
        detail = {
            'awsRegion': 'us-west-1',
            'requestParameters': {
                'resourcesSet': {
                    'items': [{'resourceId': 'i-00000000000000000'}]
                },
                'tagSet': {
                    'items': [
                        {
                            'key': 'preserve'
                        }
                    ]
                }
            },
            'responseElements': {
                '_return': True
            }
        }
        event = {
            'EventTime': '2018-06-27T17:10:13Z',
            'EventName': 'DeleteTags'
        }

        AWSResource.parse_event(detail, event, self.aws_account)
        instance = Resource.objects.get(pk=1)
        self.assertEqual(instance.preserve, None)

        # Delete instance
        detail = {
            'awsRegion': 'us-west-1',
            'responseElements': {
                'instancesSet': {
                    'items': [{'instanceId': 'i-00000000000000000'}]
                }
            }
        }
        event = {
            'EventTime': '2018-06-27T17:10:14Z',
            'EventName': 'TerminateInstances'
        }

        AWSInstance.parse_event(detail, event, self.aws_account)
        instance = Resource.objects.get(pk=1)
        self.assertNotEqual(instance.released, None)
