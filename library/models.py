import django

from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from library.amazon_account_utils import AmazonAccountUtils


# http://schinckel.net/2013/07/28/django-single-table-inheritance-on-the-cheap./
class ProxyManager(models.Manager):
    '''
    Override Manager to provide type-specific queries for the proxy classes
    '''
    def get_query_set(self):
        return super(ProxyManager, self).get_query_set().filter(
            type=self.model.__name__.lower())


class Lendable(models.Model):
    type = models.CharField(max_length=254)
    checked_out_on = models.DateTimeField(auto_now_add=True)
    due_on = models.DateTimeField()
    renewals = models.IntegerField(default=0)
    user = models.ForeignKey(User)
    credentials = None

    # The first manager assigned is the default manager for the class and its
    # subclasses. ProxyManager filters for the 'type' attribute to only load
    # records that match the subclass...
    lendables = ProxyManager()
    # ...but, we need to be able to load a collection of lendables of all types!
    # For example - everything that is checked out by a single user.
    # For this we can use the 'stock' manager.
    all_types = models.Manager()

    name = ''
    description = ''
    max_checked_out = 20
    lending_period_in_days = 14  # two weeks
    # six weeks total checkout - initial checkout plus two renewals
    max_renewals = 2

    def __init__(self, *args, **kwargs):
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
        return "%s checked out by %s" % (self.name, self.user)

    @classmethod
    def is_available_for_user(self, user):
        return (self.lendables.count() < self.max_checked_out and
            self.lendables.filter(user=user).count() == 0)

    @classmethod
    def next_available_date(self):
        try:
            next_lendable_due = self.lendables.earliest('checked_out_on')
        except ObjectDoesNotExist:
            return datetime.today()
        else:
            return next_lendable_due.due_on

    def max_due_date(self):
        return (
            self.due_on +
            timedelta(self.lending_period_in_days * self.renewals)
        )

    def is_renewable(self):
        return self.renewals > 0

    def checkout(self):
        self.checked_out_on = datetime.now(django.utils.timezone.UTC())
        self.__set_initial_due_date()
        self.renewals = settings.MAX_RENEWALS.get(self.type, self.max_renewals)

    def renew(self):
        if self.renewals > 0:
            self.renewals -= 1
            self.due_on = self.due_on + timedelta(self.lending_period_in_days)
        else:
            raise ValidationError(
                "No more renewals are available for this item."
            )
        return self.save()

    def __set_initial_due_date(self):
        """
            When a lendable is checked out, the due date is set to the checkout
            date plus the lending period.
        """
        self.due_on = (
            self.checked_out_on +
            timedelta(self.lending_period_in_days)
        )


class AmazonDemoAccount(Lendable):
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
        proxy = True

    def checkout(self):
        super().checkout()
        group = None
        try:
            group = settings.AWS_IAM_GROUP
        except:
            pass
        self.credentials = self.amazon_account_utils.create_iam_account(
            self.user.username,
            group
        )

    def checkin(self):
        self.amazon_account_utils.destroy_iam_account(self.user.username)
