"""Models used by the maile app."""

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

from django.db import models
from django.utils import formats


class EmailLog(models.Model):
    """EmailLog class used for logging emails sent by admins."""

    from_email = models.TextField(verbose_name="From")
    recipients = models.TextField()
    subject = models.CharField(max_length=120)
    body = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        """Display string for EmailLog."""
        return "%s - %s" % (formats.date_format(self.date_sent), self.subject)

    class Meta:
        """Default ordering for EmailLogs is decending (newest first)."""

        ordering = ('-date_sent',)
