"""URLs for library app."""

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

from django.conf.urls import url

from . import views

app_name = 'library'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^resource/(?P<item_subtype>\w+)/checkout$',
        views.checkout,
        name='checkout'
        ),
    url(r'^instance/(?P<primary_key>\d+)/renew$',
        views.renew,
        name='renew'
        ),
    url(r'^instance/(?P<primary_key>\d+)/checkin$',
        views.checkin,
        name='checkin'
        ),
    url(r'^instance/(?P<primary_key>\d+)/request_extension$',
        views.request_extension,
        name='request_extension'
        ),
    url(r'^login/required/$', views.require_login, name='require_login')
]
