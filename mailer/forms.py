"""Forms used by the mailer app."""

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

from django import forms
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from .constants import recipient_choices, lendable_choices


class SendMailForm(forms.Form):
    """Form for sending email to users."""

    subject = forms.CharField(max_length=120)
    to = forms.ChoiceField(choices=recipient_choices)
    lendable = forms.ChoiceField(choices=lendable_choices(), required=False)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}))

    def clean_message(self):
        """Strip message of HTML tags and leading/trailing whitespace."""
        value = self.cleaned_data['message']
        return strip_tags(value.strip())

    def clean_subject(self):
        """Strip subject of HTML tags and leading/trailing whitespace."""
        value = self.cleaned_data['subject']
        return strip_tags(value.strip())

    def clean(self):
        """Perform form wide cleaning.

        Raises:
            ValidationError: If haslendable is selected and lendable option
                is empty.
        """
        cleaned_data = super(SendMailForm, self).clean()
        to = cleaned_data.get('to')
        lendable = cleaned_data.get('lendable')

        if to == 'haslendable' and not lendable:
            self.add_error('lendable', _('This field is required.'))

        return cleaned_data
