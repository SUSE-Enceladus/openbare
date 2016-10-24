"""Template tags to check widget type for mailer app."""

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

from django import forms, template

register = template.Library()


@register.filter
def is_textarea(field):
    """Check if instance of Textarea widget."""
    return isinstance(field.field.widget, forms.Textarea)


@register.filter
def is_dropdown(field):
    """Check if instance of Select widget."""
    return isinstance(field.field.widget, forms.Select)
