from django import template
from django.template import defaultfilters


def format_date(date):
    '''
    formatted date
    '''
    return defaultfilters.date(date,"j b Y")


register = template.Library()
register.filter('format_date', format_date)

