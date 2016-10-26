"""Unit tests for mailer app."""

# Copyright © 2016 SUSE LLC.
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

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core import mail
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from library.views import index

from unittest import mock

from .models import EmailLog
from .views import email_users


class SendMailTestCase(TestCase):
    """Test mailer app."""

    def setUp(self):
        """Setup test case."""
        self.c = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="user1",
                                             email="user1@openbare.com",
                                             password="str0ngpa$$w0rd")

    def test_send_mail_auth(self):
        """Test send mail authorization.

        Test user authorization for :view:`mailer/email_users`.
        """
        request_index = self.factory.get("/index")
        request_send_mail = self.factory.get("/mail/send")

        # ## Set anonymous user
        request_index.user = request_send_mail.user = AnonymousUser()
        self.confirm_email_users_unaccessible(request_index, request_send_mail)

        # ## Set normal user
        # User is not staff or superuser
        request_index.user = request_send_mail.user = self.user
        self.confirm_email_users_unaccessible(request_index, request_send_mail)

        # ## Set staff user
        self.user.is_staff = True
        self.user.save()

        # Confirm menu item displayed
        response = index(request_index)
        self.assertContains(response, 'href="/mail/send/"', status_code=200)

        # Confirm send email view access
        response = email_users(request_send_mail)
        self.assertContains(response, '<h1>Email users</h1>', status_code=200)

    def confirm_email_users_unaccessible(self,
                                         request_index,
                                         request_send_mail):
        """Confirm AnonymousUsers and normal users cannot send email.

        Only staff and superusers have access to the email users view
        and can send emails to users.
        """
        # Confirm menu item not displayed
        response = index(request_index)
        self.assertNotContains(response, 'href="/mail/send/"', status_code=200)

        # Confirm redirect
        response = email_users(request_send_mail)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/login/?next=/mail/send')

    def test_send_mail(self):
        """Test the sending of emails to users."""
        self.user.is_staff = True
        self.user.save()

        self.c.login(username=self.user.username, password='str0ngpa$$w0rd')

        # Test required fields
        response = self.c.post('/mail/send/')
        self.assertEqual(len(response.context['form'].errors), 3)
        self.assertTrue(self.fields_required(response.context['form'],
                                             ['subject', 'message', 'to']))

        # Test lendable required when field `to` is haslendable
        context = {'to': 'haslendable'}

        response = self.c.post('/mail/send/', context)
        self.assertEqual(len(response.context['form'].errors), 3)
        self.assertTrue(self.fields_required(response.context['form'],
                                             ['subject', 'message', 'lendable']
                                             ))

        # Test no emails, email not sent
        context = {'subject': 'Test Email',
                   'to': 'haslendable',
                   'lendable': 'all',
                   'message': '<h1>Hello</h1>'
                              '<p>This is a message!</p>'
                              '<p>Thanks!</p>'
                   }

        response = self.c.post('/mail/send/', context)
        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message,
                         'No users match the current filters. '
                         'Email not sent.')
        self.assertEqual(len(mail.outbox), 0)

        # Test send email
        context['to'] = 'all'
        response = self.c.post('/mail/send/', context, follow=True)
        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, 'Email sent to 1 user(s)')
        self.assertEqual(len(mail.outbox), 1)

        # Confirm email
        self.assertEqual(mail.outbox[0].subject, 'Test Email')
        self.assertEqual(mail.outbox[0].bcc, ['<user1@openbare.com>'])
        self.assertEqual(mail.outbox[0].from_email, settings.SERVER_EMAIL)

        # HTML tags are removed for plain text only email
        self.assertEqual(mail.outbox[0].body,
                         'HelloThis is a message!Thanks!')

        # Confirm email was logged
        logs = EmailLog.objects.filter(subject='Test Email',
                                       recipients='<user1@openbare.com>',
                                       body='HelloThis is a message!Thanks!')
        self.assertEqual(len(logs), 1)

        # Confirm admin for EmailLog
        self.user.is_superuser = True
        self.user.save()

        url = reverse('admin:mailer_emaillog_change', args=(logs[0].id,))
        response = self.c.get(url)
        self.assertContains(response, 'Test Email', status_code=200)

    def field_required(self, form, field):
        """Return True if field required error exists in form."""
        return form.errors[field][0] == 'This field is required.'

    def fields_required(self, form, fields):
        """Return true if field required error exists for all fields."""
        return all([self.field_required(form, field) for field in fields])
