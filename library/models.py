"""Models for library app."""

# Copyright © 2018 SUSE LLC, James Mason <jmason@suse.com>.
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

import django
import re

from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from library.amazon_account_utils import AmazonAccountUtils

from unidecode import unidecode

from simple_history.models import HistoricalRecords


class CheckoutManager(models.Manager):
    """Override default manager to filter on checked_in_on date."""

    def get_queryset(self):
        """Filter only lendables that are checked out."""
        return super(CheckoutManager, self).get_queryset().filter(
            checked_in_on__isnull=True
        )


# http://schinckel.net/2013/07/28/django-single-table-inheritance-on-the-cheap./
class ProxyManager(CheckoutManager):
    """Override Manager to provide type-specific queries for proxy classes."""

    def get_queryset(self):
        """Return queryset of lendables that match type."""
        return super(ProxyManager, self).get_queryset().filter(
            type=self.model.__name__.lower()
        )


class Lendable(models.Model):
    """Lendable model that lendable resources extend from."""

    type = models.CharField(max_length=254)
    checked_in_on = models.DateTimeField(null=True, blank=True)
    checked_out_on = models.DateTimeField(auto_now_add=True)
    due_on = models.DateTimeField()
    notify_timer = models.FloatField(null=True, blank=True)
    renewals = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=320)
    credentials = None

    # The first manager assigned is the default manager for the class and its
    # subclasses.
    # We need to be able to load a collection of lendables of all types!
    # For example - everything that is checked out by a single user.
    # For this we can use the 'stock' manager.
    all_types = CheckoutManager()
    # ProxyManager filters for the 'type' attribute to only load
    # records that match the subclass...
    lendables = ProxyManager()
    # And provide the default manager to retrieve all checked in and
    # checked out lendables.
    all_lendables = models.Manager()

    name = ''
    description = ''
    max_checked_out = 20
    lending_period_in_days = 14  # two weeks
    # six weeks total checkout - initial checkout plus two renewals
    max_renewals = 2

    def __init__(self, *args, **kwargs):
        """Initialize Lendable instance.

        If lendable is an instance of a subclass set type to
        class name.
        """
        super(Lendable, self).__init__(*args, **kwargs)
        subclass = [
            x for x in self.__class__.__subclasses__() if (
                x.__name__.lower() == self.type
            )
        ]
        if subclass:
            self.__class__ = subclass[0]
        else:
            self.type = self.__class__.__name__.lower()

    def __str__(self):
        """Lendable string representation."""
        return "%s checked out by %s" % (self.name, self.user)

    @classmethod
    def is_available_for_user(self, user):
        """Return True if user can checkout lendable."""
        return (
            self.lendables.count() < self.max_checked_out and
            self.lendables.filter(user=user).count() == 0
        )

    @classmethod
    def next_available_date(self):
        """Return next available checkout date."""
        try:
            next_lendable_due = self.lendables.earliest('checked_out_on')
        except ObjectDoesNotExist:
            return datetime.today()
        else:
            return next_lendable_due.due_on

    def max_due_date(self):
        """Return max due date including all possible renewals."""
        return (
            self.due_on +
            timedelta(self.lending_period_in_days * self.renewals)
        )

    def is_renewable(self):
        """Return True if renewals are available."""
        return self.renewals > 0

    def checkin(self):
        """Update checkin date for lenable."""
        self.checked_in_on = datetime.now(django.utils.timezone.utc)
        self.save()

    def checkout(self):
        """Initialize checked out date, due date and renewals available."""
        if not self.is_available_for_user(self.user):
            raise Exception('{} unavailable for checkout.'.format(self.name))

        self._set_username()
        self.checked_out_on = datetime.now(django.utils.timezone.utc)
        self.__set_initial_due_date()
        self.renewals = settings.MAX_RENEWALS.get(self.type, self.max_renewals)

    def renew(self):
        """Renew lendable.

        If renewals are available update the due_on date by adding
        another period equal to lending_period_in_days.

        If no renewals available raise error and display message to user.
        """
        if self.renewals > 0:
            self.renewals -= 1
            self.due_on = self.due_on + timedelta(self.lending_period_in_days)
        else:
            raise ValidationError(
                _("No more renewals are available for this item.")
            )
        return self.save()

    def __set_initial_due_date(self):
        """Set due date when a lendable is checked out.

        When a lendable is checked out, the due date is set to the checkout
        date plus the lending period.
        """
        self.due_on = (
            self.checked_out_on +
            timedelta(self.lending_period_in_days)
        )

    def _set_username(self):
        """Set username to user.username and validate."""
        self.username = self.user.username

        # If username is invalid generate a new username. Lendable must
        # be available for checkout by user to hit this code.
        if not self._validate_username():
            self.username = get_random_string(length=20)

    def _validate_username(self):
        """Validate username.

        Length: Between 1 and 321 (accounts for emails)
        """
        return 321 > len(self.username) > 1


class AmazonDemoAccount(Lendable):
    """AWS demo account lendable."""

    name = 'Amazon Web Services - Demo Account'
    description = """\
Build your customer a comprehensive PoC without touching hardware, or launch a
hundred servers in 5 minutes for a quick experiment at scale. Amazon's public
cloud gives you access to a massive volume of resources on-demand.
"""
    # http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-limits.html
    max_checked_out = 5000

    # code that interacts with AWS (via boto3) is in a separate module, so this
    # module doesn't bloat.
    amazon_account_utils = AmazonAccountUtils(
        settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY
    )

    class Meta:
        """Proxy model of model:`library.lendable`."""

        proxy = True

    def checkout(self):
        """Checkout a demo account using IAM credentials."""
        super(AmazonDemoAccount, self).checkout()
        groups = getattr(settings, 'AWS_IAM_GROUPS', [])
        # Handle deprecated setting
        default_group = getattr(settings, 'AWS_IAM_GROUP', None)
        if default_group:
            groups.append(default_group)

        self.credentials = self.amazon_account_utils.create_iam_account(
            self.username,
            groups
        )

    def checkin(self):
        """Checkin demo account and clean up AWS resources."""
        super(AmazonDemoAccount, self).checkin()
        self.amazon_account_utils.destroy_iam_account(self.username)

    def _set_username(self):
        """Normalize username to remove none ascii chars and validate."""
        self.username = unidecode(self.user.username)

        # If username is invalid or username account already exists create
        # a new username. Lendable must be available for checkout by user
        # to hit this code.
        if not self._validate_username() or \
                self.amazon_account_utils.iam_user_exists(self.username):
            self.username = get_random_string(length=20)

    def _validate_username(self):
        """Validate username.

        Length: Between 1 and 65
        Chars: Alphanumeric including +=,.@_-
        """
        return re.match('^[\w.@+=,-]+$', self.username) and \
            65 > len(self.username) > 1


class FrontpageMessage(models.Model):
    rank = models.IntegerField(
        default=0,
        help_text='Messages are ordered by rank when listed on the front page',
        blank=False,
        db_index=True
    )
    title = models.CharField(max_length=254, blank=False)
    body = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['rank', '-updated_at']
