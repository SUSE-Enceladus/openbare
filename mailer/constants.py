"""Constants used by the mailer app."""

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

from library.models import Lendable

recipient_choices = (('', 'Send To ...'),
                     ('all', 'All users'),
                     ('haslendable', 'All users with lendables'))


def lendable_choices():
    """Generate a tuple of lendable choices.

    Returns:
        A tuple containing value/label pairs representing the
        lendable choices for a select widget.
    """
    choices = (('', 'Choose lendable ...'),
               ('all', 'All lendables'))

    choices += tuple((lendable.__name__.lower(), lendable.name)
                     for lendable in Lendable.__subclasses__())

    return choices
