# Copyright © 2017 SUSE LLC, James Mason <jmason@suse.com>.
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

from django.core.checks import register, Warning
from django.conf import settings

@register()
def deprecated_settings(app_configs, **kwargs):
    issues = []
    if ('payment_statement' in settings.HOST):
        issues.append(
            Warning(
                "The setting HOST['payment_statement'] is no longer rendered.",
                hint="Create a FrontpageMessage through the admin interface instead.",
                obj='settings.HOST',
                id='openbare.W001'
            )
        )
    if ('use_statement' in settings.HOST):
        issues.append(
            Warning(
                "The setting HOST['use_statement'] is no longer rendered.",
                hint="Create a FrontpageMessage through the admin interface instead.",
                obj='settings.HOST',
                id='openbare.W002'
            )
        )
    return issues
