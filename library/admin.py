"""Admin display options for Library app."""

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

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from library.models import Lendable
from library.models import FrontpageMessage

from simple_history.admin import SimpleHistoryAdmin


class CheckoutFilter(admin.SimpleListFilter):
    """Provide filter to query checked out and returned lendables."""
    title = _('checkout filter')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        """The options for filter(value, display)."""
        return (
            ('checkedout', _('checked out lendables')),
            ('returned', _('returned lendables')),
        )

    def queryset(self, request, queryset):
        """Filter queryset based on value."""
        if self.value() == 'checkedout':
            return queryset.filter(checked_in_on__isnull=True)

        if self.value() == 'returned':
            return queryset.filter(checked_in_on__isnull=False)


class LendableAdmin(admin.ModelAdmin):
    """Display primary key and str representation in list."""

    list_filter = (CheckoutFilter,)
    list_display = ('pk', '__str__')
    readonly_fields = (
        'checked_in_on',
        'checked_out_on',
        'type',
        'user',
        'username',
        'notify_timer'
    )

    def get_queryset(self, request):
        """Use default manager to return all lendables."""
        query_set = self.model.all_lendables.get_queryset()

        ordering = self.ordering or ()
        if ordering:
            query_set = query_set.order_by(*ordering)
        return query_set


class FrontpageMessageAdmin(SimpleHistoryAdmin):
    """List frontpage messages by rank and title"""

    list_display = ('pk', 'rank', 'title')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Lendable, LendableAdmin)
admin.site.register(FrontpageMessage, FrontpageMessageAdmin)
