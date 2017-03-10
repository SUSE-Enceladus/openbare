"""Views used by library app."""

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

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.views.generic.base import TemplateView

import base64
import json
import logging

from .templatetags import formatting_filters
from .models import Lendable
from .models import FrontpageMessage


class IndexView(TemplateView):
    """Display the openbare homepage.

    **Template:**
    :template:`library/home.html`
    """

    template_name = 'library/home.html'

    def get_context_data(self, **kwargs):
        """Return context dictionary for view."""
        context = super(IndexView, self).get_context_data(**kwargs)

        context['resources'] = get_lendable_resources(self.request.user)
        context['user_items'] = get_items_checked_out_by(self.request.user)
        context['checkout'] = False
        context['host'] = settings.HOST
        context['frontpage_messages'] = FrontpageMessage.objects.all()

        return context


def require_login(request):
    """Display warning message if user not authenticated.

    If the user manages to trigger a lendable view in an
    inactive session display a useful message and redirect
    to the index page.
    """
    messages.warning(request, 'Permission denied: You must log in.')
    return redirect(reverse('library:index'))


class CheckoutView(LoginRequiredMixin, IndexView):
    """Checkout :model:`library.Lendable` of item_subtype for user.

    Checkout a lendable of the given item_subtype for the user. The
    user is provided the necessary credentials for the lendable.

    **Template:**
    :template:`library/home.html`
    """

    redirect_field_name = None
    login_url = 'library:require_login'

    def __init__(self):
        """Initialize the view."""
        super(CheckoutView, self).__init__()
        self.item = None

    def get(self, request, *args, **kwargs):
        """Process checkout when view triggered by GET request."""
        logger = logging.getLogger('django')

        try:
            self.item = Lendable(type=self.kwargs.get('item_subtype', None),
                                 user=self.request.user)

            self.item.checkout()
            self.item.save()
        except Exception as e:
            messages.error(request, e)
            logger.exception('%s: %s' % (type(e).__name__, e))
            return redirect(reverse('library:index'))
        else:
            messages.success(
                request,
                "'%s' is checked out to you until %s." %
                (self.item.name,
                 formatting_filters.format_date(self.item.due_on))
            )

        return super(CheckoutView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Return context dictionary for view."""
        context = super(CheckoutView, self).get_context_data(**kwargs)

        context['checkout'] = True
        context['checkout_title'] = self.item.name
        context['checkout_credentials'] = self.item.credentials
        context['download_credentials_payload'] = _pack_up(
            self.item.credentials)
        context['download_credentials_filename'] = _credentials_filename(
            self.item)

        return context


@login_required(redirect_field_name=None, login_url='library:require_login')
def renew(request, primary_key):
    """Renew :model:`library.Lendable` for the length of lending_period_in_days.

    The lendable is renewed and available for another period equal to
    lending_period_in_days. Each lendable can be renewed a given amount
    of times based on the max_renewals value.

    Redirect:
    :view:`library.index`
    """
    item = get_object_or_404(Lendable.all_types,
                             pk=primary_key,
                             user=request.user)
    try:
        item.renew()
    except ValidationError as e:
        for exception_message in e.messages:
            messages.error(request, exception_message)
    except Exception as e:
        messages.error(request, e)
    else:
        messages.success(
            request,
            "'%s' is now due on %s." %
            (item.name, formatting_filters.format_date(item.due_on))
        )
    return redirect(reverse('library:index'))


@login_required(redirect_field_name=None, login_url='library:require_login')
def request_extension(request, primary_key):
    """Send email to admins to request :model:`library.Lendable` extension.

    After renewing a lendable the max available (max_renewals) times
    a user may request an extension. An email is sent to the site
    ADMINS as found in the settings for this request.

    Redirect:
    :view:`library.index`
    """
    admin_path_for_lendable = reverse(
        'admin:library_lendable_change',
        args=(primary_key,)
    )
    admin_url_for_lendable = settings.PRIMARY_URL + admin_path_for_lendable
    try:
        send_mail(
            'openbare: request to extend due_date of PK#%s' % primary_key,
            'Message from %s:\n%s\n\n%s' % (
                request.user.username,
                request.POST['message'],
                admin_url_for_lendable
            ),
            request.user.email,
            _admin_emails()
        )
    except Exception as e:
        messages.error(request, e)
    else:
        messages.success(
            request,
            'Your request was sent to the openbare Admins' +
            ' and will be evaluated.'
        )
    return redirect(reverse('library:index'))


@login_required(redirect_field_name=None, login_url='library:require_login')
def checkin(request, primary_key):
    """Checkin the :model:`library.Lendable`.

    Cleanup and delete Lendable.

    Redirect:
    :view:`library.index`
    """
    item = get_object_or_404(Lendable.all_types,
                             pk=primary_key,
                             user=request.user)
    try:
        item.checkin()
    except Exception as e:
        messages.error(request, e)
    else:
        messages.success(request, "'%s' returned." % (item.name))
        item.delete()
    return redirect(reverse('library:index'))


def get_lendable_resources(user):
    """Collect the classes of items that can be checked out.

    Their class and plugin data will be presented as
    a list of resources to 'check out'.
    """
    if not user or user.is_anonymous:
        return []

    resources = []
    for lendable in Lendable.__subclasses__():
        resources.append({
            'name': lendable.name,
            'description': lendable.description,
            'item_subtype': lendable.__name__.lower(),
            'max_checked_out': lendable.max_checked_out,
            'is_available_for_user': lendable.is_available_for_user(user),
            'next_available_date': lendable.next_available_date(),
            'checked_out_items': lendable.all_types.all(),
        })
    return resources


def get_items_checked_out_by(user=None):
    """Return the user's checked out lendables."""
    if not user or user.is_anonymous:
        return []

    return Lendable.all_types.filter(user=user).order_by('checked_out_on')


def _admin_emails():
    return ["%s <%s>" % (admin[0], admin[1]) for admin in settings.ADMINS]


def _pack_up(credentials):
    return base64.urlsafe_b64encode(
        bytes(json.dumps(credentials), encoding="UTF-8")
    )


def _credentials_filename(item):
    return slugify(
        '-'.join([
            "openbare",
            "credentials",
            str(item.pk),
            item.name
        ])
    ) + ".json"
