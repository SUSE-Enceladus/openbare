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

from django import template
from django.contrib.messages import constants as MESSAGE_LEVELS

def bootstrap_alert_class(message_level):
    classes_for_levels = {
        MESSAGE_LEVELS.INFO: 'alert-info',
        MESSAGE_LEVELS.SUCCESS: 'alert-success',
        MESSAGE_LEVELS.WARNING: 'alert-warning',
        MESSAGE_LEVELS.ERROR: 'alert-danger'
    }
    return classes_for_levels.setdefault(message_level, '')

register = template.Library()
register.filter('bootstrap_alert_class', bootstrap_alert_class)

