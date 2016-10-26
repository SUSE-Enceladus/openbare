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
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify

import base64
import json
import logging
import warnings

from .templatetags import formatting_filters
from .models import Lendable


def index(request):
    """Display the openbare homepage.

    **Template:**
    :template:`library/home.html`
    """
    context = {
        'resources': get_lendable_resources(request.user),
        'user_items': get_items_checked_out_by(request.user),
        'admin_emails': _admin_emails(),
        'checkout': False,
        'host': settings.HOST
    }
    return render(request, 'library/home.html', context=context)


def require_login(request):
    """Display warning message if user not authenticated.

    If the user manages to trigger a lendable view in an
    inactive session display a useful message and redirect
    to the index page.
    """
    messages.warning(request, 'Permission denied: You must log in.')
    return redirect(index)


@login_required(redirect_field_name=None, login_url='library:require_login')
def checkout(request, item_subtype):
    """Checkout :model:`library.Lendable` of item_subtype for user.

    Checkout a lendable of the given item_subtype for the user. The
    user is provided the necessary credentials for the lendable.

    **Template:**
    :template:`library/home.html`
    """
    logger = logging.getLogger('django')

    item = Lendable(type=item_subtype, user=request.user)
    try:
        item.checkout()
        item.save()
    except Exception as e:
        messages.error(request, e)
        logger.exception('%s: %s' % (type(e).__name__, e))
        return redirect(index)
    else:
        messages.success(
            request,
            "'%s' is checked out to you until %s." %
            (item.name, formatting_filters.format_date(item.due_on))
        )
        context = {
            'resources': get_lendable_resources(request.user),
            'user_items': get_items_checked_out_by(request.user),
            'admin_emails': _admin_emails(),
            'checkout': True,
            'checkout_title': item.name,
            'checkout_credentials': item.credentials,
            'download_credentials_payload': _pack_up(item.credentials),
            'download_credentials_filename': _credentials_filename(item)
        }

        return render(request, 'library/home.html', context=context)


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
        for exception_message in e.message_dict['renewals']:
            messages.error(request, exception_message)
    except Exception as e:
        messages.error(request, e)
    else:
        messages.success(
            request,
            "'%s' is now due on %s." %
            (item.name, formatting_filters.format_date(item.due_on))
        )
    return redirect(index)


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
    return redirect(index)


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
    return redirect(index)


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


def _verify_user(user=None):
    warnings.warn('_verify_user is deprecated and will be removed.'
                  ' Use login_required instead.', DeprecationWarning)

    if not user or user.is_anonymous:
        raise Http404


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
