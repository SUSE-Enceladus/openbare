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

from django.contrib.auth.models import AnonymousUser, User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client, RequestFactory, TestCase

from .models import Lendable
from .views import get_items_checked_out_by, get_lendable_resources, index


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

        response = index(request)
        self.assertContains(response, 'Log in', status_code=200)
        self.assertContains(response, '<h2>Welcome!</h2>', status_code=200)

    def test_require_login(self):
        """Test login required to perform lendable actions."""
        for view in ['library:checkout', 'library:renew',
                     'library:checkin', 'library:request_extension']:
            response = self.c.post(reverse(view, args=[1]), follow=True)
            self.assertContains(response,
                                'Permission denied: You must log in.',
                                status_code=200)

    def test_lendable_flow(self):
        """Test the flow of lendables."""
        self.c.login(username=self.user.username, password='str0ngpa$$w0rd')

        # Test check out lendable
        response = self.c.post(reverse('library:checkout',
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
            self.c.post(reverse('library:renew', args=[lendables[0].id]),
                        follow=True)

        renewed_lendable = Lendable.all_types.get(id=lendables[0].id)

        # Confirm the proper due on date exists and matches
        # the max_due_date for lendable resource.
        d = renewed_lendable.due_on - lendables[0].due_on
        self.assertEqual(d.days, lending_period_in_days * max_renewals)
        self.assertEqual(renewed_lendable.due_on, lendables[0].max_due_date())

        # Test no more renewals available
        response = self.c.post(reverse('library:renew',
                                       args=[lendables[0].id]),
                               follow=True)
        self.assertContains(response, 'No more renewals are available '
                                      'for this item.')

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
