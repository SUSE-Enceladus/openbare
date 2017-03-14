Django Library System - openbare
================================

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/20f6f3f39caf4bfebf280cf30c6b1f5b)](https://www.codacy.com/app/default-org/openbare?utm_source=github.com&utm_medium=referral&utm_content=openbare/openbare&utm_campaign=badger)

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


## Dependencies

* python > 3.2
* Django ~= 1.10.0
* python-social-auth
* django-markdown-deux
* django-split-settings
* django-simple-history
* boto3
* unidecode

### Optional for development

* django-debug-toolbar
* flake8
* coverage


## Setting up a development environment

#### For openSUSE and SUSE Linux Enterprise

*   Add a repository from OBS
    [devel:languages:python3](https://build.opensuse.org/project/show/devel:languages:python3)
    appropriate for your distribution to your system.

*   Install all dependencies
    ```
    zypper in python3-Django python3-python-social-auth \
      python3-django-debug-toolbar python3-django-markdown-deux \
      python3-django-split-settings python3-boto3 python3-Unidecode \
      python3-coverage

    sudo pip install django-simple-history
    ```

#### Alternative: Using pip and/or virtualenv

See the [python-guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
for setting up and activating a virtualenv.

##### Install dependencies

```
pip install -r requirements/dev.txt
```

### Initializing your environment

1. Fork openbare to your GitHub account

1. Clone the repository
    ```
    git clone git@github.com:{username}/openbare.git
    ```

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
    python3 manage.py loaddata
    python3 manage.py createsuperuser
    ```

1.  Test-run the server
    ```
    python3 manage.py runserver
    ```

    Browse to `http://localhost:8000`


## Setting up a production instance with Apache and Postrgres on SLES 12 SP1

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
    # Add 'wsgi' to APACHE_MODULES
    edit /etc/sysconfig/apache2

    # Verify
    apachectl -M | grep wsgi

    # Create a new config
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


## Lendable Resources

### AWS IAM Accounts

The AWS resource allows users to checkout IAM credentials for use with
Amazon Web Services. The IAM accounts are checked out using the
credential information provided in the Django settings files. To enable
access for AWS the following settings should be updated with the
correct account information:

```
# Amazon Web Services API credentials
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_ACCOUNT_ID_ALIAS = ''

# Optional: Users are added to the following IAM group
AWS_IAM_GROUP = ''
```

### Adding a resource

All resources are proxy classes extending from the Lendable model. To
add a resource for *openbare* override the name/description values and
the checkout/checkin methods.

Optionally, the _set_username and _validate_username methods can be
overridden to provide resource specific username validation.

## Contributing

If you would like to make contributions to *openbare* please fork the
code on GitHub and submit a pull request with your changes. Please
submit an issue if you experience any problems, bugs or have
enhancement requests. See below for more information on code format,
testing and release versions.

### Code format and testing

*openbare* uses flake8 formatting for code consistency. Prior to a pull
request run flake8 to ensure there are no warnings.

```
flake8                     # To check the entire project
flake8 libarary/models.py  # To check a specific file
```

Additionally, all code changes and additions require unit tests. Pull
requests should maintain the current code coverage and all tests must
pass.

```
python manage.py test
```

To check code coverage in Django run the following commands:

```
coverage run --source='.' manage.py test  # Run unit tests
coverage report                           # Generate report
coverage html                             # Generate HTML report
```

More information can be found on [readthedocs](https://coverage.readthedocs.io/en/coverage-4.2/)
for the coverage package.

### Versions & Releases

*openbare* adheres to Semantic versioning; see http://semver.org/ for details.

[*bumpversion*](https://pypi.python.org/pypi/bumpversion/) is used for release
version management, and configured in `setup.cfg`:

```
# bumpversion major|minor|patch
# git push && git push --tags
```


## Useful Links

* Getting started with Django: https://www.djangoproject.com/start/
* About Python 3: https://docs.djangoproject.com/en/1.8/topics/python3/
* OpenID authentication module: http://psa.matiasaguirre.net/
* Twitter Bootstrap UI framework: http://getbootstrap.com/getting-started/
* 'Yeti' theme: http://bootswatch.com/yeti/
* FontAwesome icons: http://fontawesome.io/examples/ http://fontawesome.io/cheatsheet/


## License

This project is licensed under the GNU General Public License - see the
[LICENSE](LICENSE) file for details.
