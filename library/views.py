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
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import slugify

import base64
import json

from library.templatetags import formatting_filters
from library.models import *


def index(request):
    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'resources': get_lendable_resources(request.user),
        'user_items': get_items_checked_out_by(request.user),
        'admin_emails': _admin_emails(),
        'checkout': False,
        'host': settings.HOST
    })
    return render_to_response('library/home.html', context_instance=context)


def checkout(request, item_subtype):
    _verify_user(request.user)

    item = Lendable(type=item_subtype, user=request.user)
    try:
        item.checkout()
        item.save()
    except Exception as e:
        messages.error(request, e)
        return redirect(index)
    else:
        messages.success(
            request,
            "'%s' is checked out to you until %s." %
            (item.name, formatting_filters.format_date(item.due_on))
        )
        context_dict = {
            'request': request,
            'user': request.user,
            'resources': get_lendable_resources(request.user),
            'user_items': get_items_checked_out_by(request.user),
            'admin_emails': _admin_emails(),
            'checkout': True,
            'checkout_title': item.name,
            'checkout_credentials': item.credentials,
            'download_credentials_payload': _pack_up(item.credentials),
            'download_credentials_filename': _credentials_filename(item)
        }
        context = RequestContext(request, context_dict)
        return render_to_response(
            'library/home.html',
            context_instance=context
        )


def renew(request, primary_key):
    _verify_user(request.user)

    item = get_object_or_404(Lendable.all_types, pk=primary_key, user=request.user)
    try:
        item.renew()
    except ValidationError as e:
        for exception_message in e.message_dict[NON_FIELD_ERRORS]:
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


def request_extension(request, primary_key):
    _verify_user(request.user)

    item = get_object_or_404(
        Lendable.all_types,
        pk=primary_key,
        user=request.user
    )

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


def checkin(request, primary_key):
    _verify_user(request.user)

    item = get_object_or_404(Lendable.all_types, pk=primary_key, user=request.user)
    try:
        item.checkin()
    except Exception as e:
        messages.error(request, e)
    else:
        messages.success(request, "'%s' returned." % (item.name))
        item.delete()
    return redirect(index)


def get_lendable_resources(user):
    '''
    Collect the classes of items that can be checked out; their class and
    plugin data will be presented as a list of resources to 'check out'.
    '''
    if (not user or user.is_anonymous()):
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
    if (not user or user.is_anonymous()):
        return []

    return Lendable.all_types.filter(user=user).order_by('checked_out_on')


def _verify_user(user=None):
    if (not user or user.is_anonymous()):
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
