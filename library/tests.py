""""Tests for library app."""

# Copyright © 2016 SUSE LLC, James Mason <jmason@suse.com>.
#
# This file is part of openbare.
#
# openbare is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# openbare is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with openbare. If not, see <http://www.gnu.org/licenses/>.

from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser, User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client, RequestFactory, TestCase

from library.models import AmazonDemoAccount, Lendable
from library.views import (get_items_checked_out_by, get_lendable_resources,
                           IndexView)

from library.amazon_account_utils import AmazonAccountUtils
from library.mock_aws.aws_endpoints import AWSMock
from library.mock_aws.constants import fake_user_name


class LibraryTestCase(TestCase):
    """Test library app."""

    def setUp(self):
        """Setup test case."""
        self.c = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="user1",
                                             email="user1@openbare.com",
                                             password="str0ngpa$$w0rd")

    def test_index(self):
        """Test index view."""
        request = self.factory.get("/index")
        request.user = AnonymousUser()

        view = IndexView.as_view()
        response = view(request)
        self.assertContains(response, 'Log in', status_code=200)
        self.assertContains(response, '<h2>Welcome!</h2>', status_code=200)

    def test_require_login(self):
        """Test login required to perform lendable actions."""
        for view in ['library:checkout', 'library:renew',
                     'library:checkin', 'library:request_extension']:
            response = self.c.get(reverse(view, args=[1]), follow=True)
            self.assertContains(response,
                                'Permission denied: You must log in.',
                                status_code=200)

    def test_lendable_flow(self):
        """Test the flow of lendables."""
        self.c.login(username=self.user.username, password='str0ngpa$$w0rd')

        # Test check out lendable
        response = self.c.get(reverse('library:checkout',
                                      args=['lendable']),
                              follow=True)

        self.assertContains(response, 'is checked out to you',
                            status_code=200)
        self.assertEqual(Lendable.all_types.count(), 1)

        # Test get lendables for user
        lendables = get_items_checked_out_by(self.user)
        self.assertEqual(len(lendables), 1)

        # Test renew lendable, renew the max amount of times
        max_renewals = lendables[0].max_renewals
        lending_period_in_days = lendables[0].lending_period_in_days

        for i in range(max_renewals):
            self.c.get(reverse('library:renew', args=[lendables[0].id]),
                       follow=True)

        renewed_lendable = Lendable.all_types.get(id=lendables[0].id)

        # Confirm the proper due on date exists and matches
        # the max_due_date for lendable resource.
        d = renewed_lendable.due_on - lendables[0].due_on
        self.assertEqual(d.days, lending_period_in_days * max_renewals)
        self.assertEqual(renewed_lendable.due_on, lendables[0].max_due_date())

        # Test no more renewals available
        response = self.c.get(reverse('library:renew',
                                      args=[lendables[0].id]),
                              follow=True)
        self.assertContains(response, 'No more renewals are available '
                                      'for this item.')

        # Test renew catches generic exception
        with patch.object(Lendable,
                          'renew',
                          side_effect=Exception('Renew Failed!')):
            response = self.c.get(reverse('library:renew',
                                          args=[lendables[0].id]),
                                  follow=True)

        # Confirm error message displayed
        message = list(response.context['messages'])[0].message
        self.assertEqual(message, 'Renew Failed!')

        # Test request extension
        with self.settings(ADMINS=[('John', 'john@example.com')]):
            response = self.c.post(reverse('library:request_extension',
                                           args=[lendables[0].id]),
                                   {'message': 'Extend me!'},
                                   follow=True)

        self.assertContains(response,
                            'Your request was sent to the openbare Admins'
                            ' and will be evaluated.')
        self.assertEqual(len(mail.outbox), 1)

        # Test request extension catches generic exception
        with patch('library.views._admin_emails',
                   side_effect=Exception('Email Failed!')):
            response = self.c.post(reverse('library:request_extension',
                                           args=[lendables[0].id]),
                                   {'message': 'Extend me!'},
                                   follow=True)

        # Confirm error message displayed
        message = list(response.context['messages'])[0].message
        self.assertEqual(message, 'Email Failed!')

    def test_checkout_exception(self):
        self.c.login(username=self.user.username, password='str0ngpa$$w0rd')

        # Test check out lendable raises exception
        with patch.object(Lendable,
                          'checkout',
                          side_effect=Exception('Checkout Failed!')):
            response = self.c.get(reverse('library:checkout',
                                          args=['lendable']),
                                  follow=True)

        # Confirm error message displayed
        message = list(response.context['messages'])[0].message
        self.assertEqual(message, 'Checkout Failed!')

        # Confirm lendable not created
        self.assertEqual(Lendable.all_types.count(), 0)

    def test_get_lendable_resources(self):
        """Test get_lendable_resources method."""
        # Anonymous or None user should return an empty set
        resources = get_lendable_resources(AnonymousUser())
        self.assertEqual(resources, [])

        resources = get_lendable_resources(self.user)

        # Confirm AWS resource is available
        aws = list(filter(
            lambda resource: resource['item_subtype'] == 'amazondemoaccount',
            resources))
        self.assertEqual(len(aws), 1)

    def test_get_items_checked_out_by(self):
        """Test get_items_checked_out_by method."""
        lendables = get_items_checked_out_by(None)
        self.assertEqual(lendables, [])

        lendables = get_items_checked_out_by(AnonymousUser())
        self.assertEqual(lendables, [])

    def test_username_generated(self):
        self.lendable = Lendable(user=self.user)

        # Test random username is generated when len(username) > 321.
        self.user.username = 'a' * 322
        self.lendable._set_username()
        self.assertNotEqual(self.lendable.username, self.user.username)
        self.assertEqual(len(self.lendable.username), 20)


class AWSTestCase(TestCase):
    """Test library app."""

    def setUp(self):
        """Setup user and account instances."""
        self.c = Client()
        self.user = User.objects.create_user(username="Jőhn",
                                             email="user1@openbare.com",
                                             password="str0ngpa$$w0rd")
        self.aws_account = AmazonDemoAccount(user=self.user)

    def test_validate_username(self):
        """Test validate username method."""
        # Test empty string
        self.aws_account.username = ''
        self.assertFalse(self.aws_account._validate_username())

        # Test name > 64
        self.aws_account.username = 't' * 65
        self.assertFalse(self.aws_account._validate_username())

        # Test valid string
        self.aws_account.username = 'testname'
        self.assertTrue(self.aws_account._validate_username())

        # Test invalid character
        self.aws_account.username = 'testname!'
        self.assertFalse(self.aws_account._validate_username())

    def test_set_username(self):
        """Test set username method."""
        # Test unicode converts to ascii Jőhn to John
        with patch.object(AmazonAccountUtils,
                          'iam_user_exists',
                          return_value=False):
            self.aws_account._set_username()
            self.assertEqual(self.aws_account.username, 'John')

        # Test random username generated if iam user exists
        with patch.object(AmazonAccountUtils,
                          'iam_user_exists',
                          return_value=True):
            self.aws_account._set_username()
            self.assertNotEqual(self.aws_account.username, 'John')
            self.assertEqual(len(self.aws_account.username), 20)

        # Test random username is generated when regex invalid
        # after conversion. ʢʢʢ converts to ???.
        self.user.username = 'ʢʢʢ'
        self.aws_account._set_username()
        self.assertNotEqual(self.aws_account.username, '???')
        self.assertEqual(len(self.aws_account.username), 20)

    def test_aws_checkout(self):
        """Test AWS IAM checkout and checkin.

        Mock cleanup method with a return value of True.
        """
        self.c.login(username=self.user.username, password='str0ngpa$$w0rd')
        mocker = AWSMock()
        mocker.create_group({'GroupName': 'Admins'})

        # Checkout AWS account
        with self.settings(AWS_ACCOUNT_ID_ALIAS='John.Wayne',
                           AWS_IAM_GROUP='Admins'):
            with patch('botocore.client.BaseClient._make_api_call',
                       new=mocker.mock_make_api_call):
                # Test check out AWS lendable
                response = self.c.get(reverse('library:checkout',
                                              args=['amazondemoaccount']),
                                      follow=True)

        # Get lendable and parse due date string
        aws_lendable = self.user.lendable_set.first()
        date_str = aws_lendable.due_on.strftime("%-d %b %Y").lower()

        # Confirm sucess message displayed
        message = list(response.context['messages'])[0].message
        self.assertEqual("'Amazon Web Services - Demo Account' "
                         "is checked out to you until %s." % date_str,
                         message)

        # Confirm credential values displayed in modal
        self.assertContains(response, '<code>John</code>')
        self.assertContains(response,
                            'https://John.Wayne.signin.aws.amazon.com/console')

        # Confirm lendable created
        self.assertEqual(Lendable.all_types.count(), 1)

        # Test user cannot checkout AWS account twice
        response = self.c.get(reverse('library:checkout',
                                      args=['amazondemoaccount']),
                              follow=True)

        # Confirm error message displayed
        message = list(response.context['messages'])[0].message
        self.assertEqual(message,
                         "Amazon Web Services - Demo Account "
                         "unavailable for checkout.")

        # Confirm lendable not created
        self.assertEqual(Lendable.all_types.count(), 1)

        # Get lendable primary key
        pk = self.user.lendable_set.first().id

        # Test checkin handles generic exception
        with patch.object(AmazonDemoAccount,
                          'checkin',
                          side_effect=Exception('Checkin Failed!')):
            response = self.c.get(reverse('library:checkin',
                                          args=[pk]),
                                  follow=True)

        # Confirm error message displayed
        message = list(response.context['messages'])[0].message
        self.assertEqual(message, 'Checkin Failed!')

        # Checkin AWS account
        with patch('botocore.client.BaseClient._make_api_call',
                   new=mocker.mock_make_api_call):
            # Test check in AWS lendable
            response = self.c.get(reverse('library:checkin',
                                          args=[pk]),
                                  follow=True)

        # Confirm success message displayed
        message = list(response.context['messages'])[0].message
        self.assertEqual("'Amazon Web Services - Demo Account' returned.",
                         message)

        # Confirm lendable deleted
        self.assertEqual(Lendable.all_types.count(), 0)

        mocker.delete_group({'GroupName': 'Admins'})

    def test_checkout_group_exception(self):
        mocker = AWSMock()
        self.c.login(username=self.user.username, password='str0ngpa$$w0rd')

        # Test create IAM account group not found exception handled
        with patch('botocore.client.BaseClient._make_api_call',
                   new=mocker.mock_make_api_call):
            with self.settings(AWS_IAM_GROUP='Admins',
                               AWS_ACCOUNT_ID_ALIAS=None):
                response = self.c.get(reverse('library:checkout',
                                              args=['amazondemoaccount']),
                                      follow=True)

        # Confirm error message displayed
        message = list(response.context['messages'])[0].message
        self.assertEqual(message,
                         "An error occurred (Not Found) when calling the "
                         "AddUserToGroup operation: Group Admins not found")

        # Confirm lendable not created
        self.assertEqual(Lendable.all_types.count(), 0)

    def test_checkout_exception(self):
        """Test exception from create IAM account is handled properly."""
        mocker = AWSMock()
        self.user.username = fake_user_name
        self.user.save()

        self.c.login(username=self.user.username, password='str0ngpa$$w0rd')

        # Test create IAM account exception handled
        with patch('botocore.client.BaseClient._make_api_call',
                   new=mocker.mock_make_api_call):
            with patch.object(AmazonAccountUtils,
                              '_cleanup_iam_user',
                              return_value=True):
                response = self.c.get(reverse('library:checkout',
                                              args=['amazondemoaccount']),
                                      follow=True)

        # Confirm error message displayed
        message = list(response.context['messages'])[0].message
        self.assertEqual(message,
                         "An error occurred (Error) when calling the "
                         "CreateUser operation: User creation failed")

        # Confirm lendable not created
        self.assertEqual(Lendable.all_types.count(), 0)

    def test_checkin_404(self):
        self.c.login(username=self.user.username, password='str0ngpa$$w0rd')

        response = self.c.get(reverse('library:checkin',
                                      args=[1]),
                              follow=True)

        # Confirm 404 displayed
        self.assertEqual(response.status_code, 404)

    def test_destroy_account_not_exist(self):
        mocker = AWSMock()
        with patch('botocore.client.BaseClient._make_api_call',
                   new=mocker.mock_make_api_call):
            amazon_account_utils = AmazonAccountUtils(
                '43543253245',
                '6543654rfdfds'
            )
            result = amazon_account_utils.destroy_iam_account('john')

        self.assertFalse(result)
