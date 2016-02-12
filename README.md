SUSE Public Cloud Demo Account Library - openbare
=================================================

A library app, allowing 'check out' of a demo account in any framework, for a
predefined time period. Administrators can manage all demo accounts centrally.


Prerequisites
-------------

* python > 3.2
* [devel:languages:python3](https://build.opensuse.org/project/show/devel:languages:python3)
  repository from OBS
* Django ~ 1.8.4 (`zypper in python3-Django`)
* python-social-auth (`zypper in python3-python-social-auth`)
  ** **WARNING**: we are subject to https://github.com/omab/python-social-auth/issues/617
* django-debug-toolbar (`zypper in python3-django-debug-toolbar`)
* django-markdown-deux (`zypper in python3-django-markdown-deux`)
* django-split-settings (`zypper in python3-django-split-settings`)
* boto3 (`zypper in python3-boto3`)


Initializing your development environment
-----------------------------------------

1.  Get in position
    ```
    cd pubcloud/generic/src/openbare
    ```

1.  Create your local settings
    ```
    cp openbare/settings/local_development.py.template \
    openbare/settings/local_development.py
    edit openbare/settings/local_development.py
    ```

1.  Setup the database
    ```
    python3 manage.py migrate
    python3 manage.py createsuperuser
    ```

1.  Test-run the server
    ```
    python3 manage.py runserver
    ```

    Browse to `http://localhost:8000`

1.  Log into the admin interface and create a resource.

  1.  Browse to `http://localhost:8000/admin/library/resource` .
      You will be redirected to the login page.
  2.  Log in with the superuser credentials you created when you setup the database.
  3.  Click 'Add resource'
  4.  Fill out the form, and click 'Save'

You may now browse to the application URL (`http://localhost:8000`), login
with your Novell Login, and use the application.

Useful Links
------------

* Getting started with Django: https://www.djangoproject.com/start/
* About Python 3: https://docs.djangoproject.com/en/1.8/topics/python3/
* OpenID authentication module: http://psa.matiasaguirre.net/
* Twitter Bootstrap UI framework: http://getbootstrap.com/getting-started/
* 'Yeti' theme: http://bootswatch.com/yeti/
* FontAwesome icons: http://fontawesome.io/examples/ http://fontawesome.io/cheatsheet/
