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
from library.models import Lendable
from library.models import FrontpageMessage


class LendableAdmin(admin.ModelAdmin):
    """Display primary key and str representation in list."""

    list_display = ('pk', '__str__')
    readonly_fields = ('type', 'user', 'username', 'notify_timer')

class FrontpageMessageAdmin(admin.ModelAdmin):
    """List frontpage messages by rank and title"""

    list_display = ('pk', 'rank', 'title')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Lendable, LendableAdmin)
admin.site.register(FrontpageMessage, FrontpageMessageAdmin)
