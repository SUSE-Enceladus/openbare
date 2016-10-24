"""Mailer admin display options."""

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

from django.contrib import admin
from django.template.defaultfilters import linebreaksbr

from .models import EmailLog


class EmailLogAdmin(admin.ModelAdmin):
    """Enable EmailLogs in the admin panel.

    Admin for EmailLog is only viewable. The addition
    and deletion of EmailLogs is not permitted.
    """

    list_display = ['__str__', 'from_email', 'subject', 'date_sent']
    list_filter = ['date_sent']
    search_fields = ['subject', 'body', 'recipients']
    readonly_fields = ['from_email', 'recipients', 'subject',
                       'body_display', 'date_sent']
    exclude = ['body']

    def body_display(self, obj):
        """Convert all newlines to HTML line breaks."""
        return linebreaksbr(obj.body)
    body_display.short_description = "body"

    def has_delete_permission(self, *args, **kwargs):
        """Disable deletion of EmailLogs in admin."""
        return False

    def has_add_permission(self, *args, **kwargs):
        """Disable adding EmailLogs in admin."""
        return False


admin.site.register(EmailLog, EmailLogAdmin)
