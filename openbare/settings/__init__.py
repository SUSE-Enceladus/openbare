from split_settings.tools import optional, include

# Settings are split using split_settings:
# https://github.com/sobolevn/django-split-settings
#
# * Universal settings for openbare live in settings.base.
# * All local settings are imported as well, and supercede base settings.
#   Keep your dev settings here. A template is provided for getting you started:
#   settings/local_development.py.template
# * System-wide settings not appropriate for settings.base belong in
#   /etc/openbare/settings_*.py
# * Templates are provided for public setting files for:
#   DB, Session Secret, AWS, Logging.

include(
    "base.py", # was settings.py
    optional("local_*.py"), # def settings - ignored by git
    optional("/etc/openbare/settings_*.py"), # production settings
    scope=locals()
)
