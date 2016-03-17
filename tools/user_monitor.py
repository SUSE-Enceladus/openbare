#!/usr/bin/env python
#
# Copyright © 2016 SUSE LLC, Robert Schweikert <rjschwei@suse.com>,
# James Mason <jmason@suse.com>.
#
# This file is part of SUSE openbare.
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

import os
from datetime import datetime
import django
from django.core.mail import send_mail
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openbare.settings")
django.setup()

from library.models import *


def checkin_expired_accounts():
    now = datetime.now(django.utils.timezone.UTC())
    for lendable in Lendable.all_types.filter(due_on__lte=now):
        lendable.checkin()


def get_warning_message(lendable):
    return """
Hi %(firstname)!

You have an item checked out via openbare that's going to expire soon.

'%(lendable)' is due on '%(due_date)'. Unless you renew it or request an
extension, the item will automatically be returned, and we'll clean up any
mess you left.

If you'd like to take some action, you can visit openbare at:
%(primary_url)

Have a great day!
- Your openbare Admins
""" % {
            'firstname': lendable.user.firstname,
            'lendable': lendable.__str__(),
            'due_date': lendable.due_date(),
            'primary_url': settings.PRIMARY_URL,
        }


def notify_user():
    now = datetime.now(django.utils.timezone.UTC())
    for days in django.settings.EXPIRATION_NOTIFICATION_WARNING_DAYS:
        lendables = Lendable.all_types.get(
            Q(due_on__lte=now + timedelta(days)) &
            (
                Q(notify_timer=None) |
                Q(notify_timer__gt=days)
            )
        )
        for lendable in lendables:
            try:
                send_mail(
                    'Expiration warning',
                    get_warning_message(lendable),
                    'openbare-admins@susecloud.net',
                    lendable.user.email
                )
            except Exception as e:
                logging.error(e)
            else:
                delta = (lendable.due_on - now)
                # 86400 seconds/day - timedelta as float of days
                lendable.notify_timer = delta.days + delta.seconds / 86400
                lendable.save()


def start_logging():
    """Set up logging"""
    log_filename = '/var/log/openbare_user_monitor'
    try:
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
    except IOError:
        print 'Could not open log file ', logFile, ' for writing.'
        sys.exit(1)

start_logging()
checkin_expired_accounts()
notify_user()
