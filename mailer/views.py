"""Views used by mailer app."""

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
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render

from .forms import SendMailForm
from .models import EmailLog


@staff_member_required
def email_users(request):
    """
    Display and process send mail form.

    Provides a view to send email to users based on the
    selected filters. When successfully sent
    the email is logged using the :model:`mailer.EmailLog`.

    ** Template: **
    :template:`mailer/email_users.html`

    """
    if request.method == 'POST':
        form = SendMailForm(request.POST)

        if form.is_valid():
            # Get list of Emails
            emails = get_user_emails(form.cleaned_data['to'],
                                     form.cleaned_data['lendable'])

            if len(emails):
                from_email = settings.SERVER_EMAIL

                try:
                    # Send email
                    EmailMessage(
                        subject=form.cleaned_data['subject'],
                        body=form.cleaned_data['message'],
                        from_email=from_email,
                        bcc=emails
                    ).send()

                except Exception as e:
                    messages.error(request, "Failed to send email: %s" % e)

                else:
                    messages.success(request,
                                     "Email sent to %d user(s)" % len(emails))

                    # Log email for future reference
                    EmailLog.objects.create(
                        from_email=from_email,
                        recipients=', '.join(emails),
                        subject=form.cleaned_data['subject'],
                        body=form.cleaned_data['message'],
                    )

                    return redirect(reverse('home'))

            else:
                # Email list is empty
                messages.warning(request,
                                 "No users match the current filters. "
                                 "Email not sent.")

    else:
        form = SendMailForm()

    return render(request, 'mailer/email_users.html', {'form': form})


def get_user_emails(recipient, lendable):
    """Retrieve list of user emails given filter criteria.

    Returns:
        A list of emails formatted as `first_name last_name <email>`.
    """
    # Filter all users that have an email
    emails = User.objects.filter(is_active=True).exclude(email__exact='')

    if recipient == 'haslendable':
        if lendable == 'all':
            # Filter all users with any lendable checked out
            emails = emails.filter(lendable__isnull=False)
        else:
            # Filter all users with `lendable` checked out
            emails = emails.filter(lendable__type=lendable)

    # Retrieves a list of dictionaries with user first, last and email
    emails = emails.values('first_name', 'last_name', 'email')

    # Return email list. Split then join removes extra whitespace
    # for users that don't have a first and/or last name.
    return [' '.join(
        '{first} {last} <{email}>'.format(first=email['first_name'],
                                          last=email['last_name'],
                                          email=email['email']).split()
                    ) for email in emails]
