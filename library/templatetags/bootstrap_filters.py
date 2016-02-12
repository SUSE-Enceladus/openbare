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

