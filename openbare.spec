#
# spec file for package openbare
#
# Copyright (c) 2016 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

Name:           openbare
Version:        0.5.1
Release:        0
Summary:        A digital asset library system, implemented on Django
License:        GPL-3.0
Group:          Applications/Internet
Url:            https://github.com/openbare/openbare
Source0:        %{name}-%{version}.tar.bz2
Requires:       python3
Requires:       python3-Django
Requires:       python3-python-social-auth
Requires:       python3-django-markdown-deux
Requires:       python3-django-split-settings
Requires:       python3-boto3
BuildRequires:  fdupes
Recommends:     python3-django-debug-toolbar
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

%description
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

%prep
%setup -q -n %{name}-%{version}

%build

%install
%make_install
%fdupes %{buildroot}/srv/www/%{name}

%files
%doc LICENSE README.md
%attr(-, wwwrun, www) /srv/www/%{name}
%attr(0750, root, root) /usr/sbin/openbare-manage
%attr(0750, root, root) /usr/sbin/openbare-user-monitor
%config(noreplace) /etc/%{name}
%{_mandir}/man*/*

%changelog
