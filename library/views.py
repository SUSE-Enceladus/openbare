from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.template.context import RequestContext
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.http import Http404

from library.templatetags import formatting_filters
from .models import *


def index(request):
    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'resources': get_lendable_resources(request.user),
        'user_items': get_items_checked_out_by(request.user),
        'checkout': False
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
            (item.name, formatting_filters.format_date(item.due_date()))
        )
        context_dict = {
            'request': request,
            'user': request.user,
            'resources': get_lendable_resources(request.user),
            'user_items': get_items_checked_out_by(request.user),
            'checkout': True,
            'checkout_title': item.name,
            'checkout_credentials': item.credentials
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
            (item.name, formatting_filters.format_date(item.due_date()))
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

