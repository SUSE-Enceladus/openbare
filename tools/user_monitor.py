# Copyright © 2016 SUSE LLC, James Mason <jmason@suse.com>.
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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openbare.settings")
django.setup()

from library.models import *


def checkin_expired_accounts():
    now = datetime.now(django.utils.timezone.UTC())
    for lendable in Lendable.all_types.filter(due_on__lte = now)
        lendable.checkin()

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
            #send_an_email()
            delta = (lendable.due_on - now)
            # 86400 seconds/day - timedelta as float of days
            lendable.notify_timer = delta.days + delta.seconds / 86400
            lendable.save()

checkin_expired_accounts()
notify_user()
