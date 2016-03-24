Django Library System - openbare
=================================================

openbare is a digital asset library system, implemented on Django.

The system started out with the intend to provide access to Public Cloud
accounts for everyone at SUSE. At the onset of the project is was hoped that
implementation of the framework could be sufficiently generalized to provide
functionality for pretty much anything that one might keep track of that
fits the concept of a Public Library. Once the first plugin was developed
to manage AWS IAM access this hope was realized and the project moved from
a private repository to a public repository in the hopes that others will
find the system useful and will contribute back to the project.

We'd like to thank SUSE for sponsoring our work and enabling us to set up the
project in a company independent way.


Dependencies
------------

* python > 3.2
* Django ~ 1.8.4
* python-social-auth
* django-debug-toolbar
* django-markdown-deux
* django-split-settings
* boto3

For openSUSE and SUSE Linux Enterprise
--------------------------------------
*   Add a repository from OBS
    [devel:languages:python3](https://build.opensuse.org/project/show/devel:languages:python3)
    appropriate for your distribution to your system.

*   Install all dependencies
    ```
    zypper in python3-Django python3-python-social-auth \
      python3-django-debug-toolbar python3-django-markdown-deux \
      python3-django-split-settings python3-boto3
    ```

Initializing your development environment
-----------------------------------------

1.  Get in position
    ```
    cd openbare
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


Setting up a production instance with Apache and Postrgres on SLES 12 SP1
-------------------------------------------------------------------------

1.  As root...
    ```
    sudo -i
    ```

1.  Install Apache and Postgresql
    ```
    zypper ar --refresh http://download.opensuse.org/repositories/devel:/languages:/python3/SLE_12_SP1/devel:languages:python3.repo
    zypper ar --refresh http://download.opensuse.org/repositories/Apache:/Modules/SLE_12_SP1/Apache:Modules.repo
    zypper in apache apache2-mod_wsgi-python3 postgresql94-server python3-psycopg2
    ```

1.  Install openbare
    ```
    # temporary home of openbare
    zypper in --no-recommends http://download.opensuse.org/repositories/home:/bear454/SLE_12_SP1/noarch/openbare-0.2.0-1.1.noarch.rpm
    ```

1.  Setup Postgresql
    ```
    systemctl enable postgresql
    systemctl start postgresql
    su - postgres
    createdb openbare
    psql
    CREATE ROLE openbare WITH PASSWORD "[secret-database-password]";
    ALTER ROLE openbare WITH LOGIN;
    CREATE DATABASE openbare WITH OWNER openbare;
    GRANT ALL PRIVILEGES ON DATABASE openbare TO openbare;
    \q
    logout
    ```

1.  Setup Apache
    ```
    edit /etc/sysconfig/apache2 # add 'wsgi' to APACHE_MODULES
    # verify
    apachectl -M | grep wsgi
    # create a new config
    mv /etc/apache2/default-server.conf /etc/apache2/default-server.conf.orig
    echo "
    # Static Assets
    ## directly serve admin assets from the django module
    Alias /static/admin /usr/lib/python3.4/site-packages/django/contrib/admin/static/admin
    ## directly serve openbare's assets
    Alias /static /srv/www/openbare/static
    <Directory /usr/lib/python3.4/site-packages/django/contrib/admin/static/admin>
    Require all granted
    Options FollowSymLinks
    </Directory>
    <Directory /srv/www/openbare/static>
    Require all granted
    Options FollowSymLinks
    </Directory>

    # Setup WSGI server
    WSGIScriptAlias / /srv/www/openbare/openbare/wsgi.py
    WSGIPythonPath /srv/www/openbare
    <Directory /srv/www/openbare>
    <Files wsgi.py>
    Require all granted
    </Files>
    </Directory>
    " > /etc/apache2/default-server.conf
    systemctl enable apache2
    ```

1.  Configure openbare
    ```
    for file in /etc/openbare/settings_*.py.template; do cp "$file" "${file%.template}"; done
    edit /etc/openbare/settings_*.py
    openbare-manage migrate
    openbare-manage createsuperuser
    ```

1.  Start Apache!
    ```
    systemctl start apache2
    ```

Useful Links
------------

* Getting started with Django: https://www.djangoproject.com/start/
* About Python 3: https://docs.djangoproject.com/en/1.8/topics/python3/
* OpenID authentication module: http://psa.matiasaguirre.net/
* Twitter Bootstrap UI framework: http://getbootstrap.com/getting-started/
* 'Yeti' theme: http://bootswatch.com/yeti/
* FontAwesome icons: http://fontawesome.io/examples/ http://fontawesome.io/cheatsheet/
