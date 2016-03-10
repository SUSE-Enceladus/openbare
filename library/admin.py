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

from django.contrib import admin
from library.models import Lendable
# Register your models here.


class LendableAdmin(admin.ModelAdmin):
    list_display = ('pk', '__str__')


admin.site.register(Lendable, LendableAdmin)
