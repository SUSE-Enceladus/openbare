""""Mocked endpoints."""

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

import re

from django.utils.crypto import get_random_string

from .aws_responses import (access_key_response, client_error,
                            group_response, delete_response,
                            list_access_keys_response,
                            list_attached_policies_response,
                            list_mfa_devices_response,
                            list_signing_certs_response,
                            list_user_groups_response, login_profile_response,
                            user_response, user_group_response)
from .constants import group_name, fake_user_name, username


def inflection(name):
    """Convert camelcase names into snakecase attributes.

    CreateUser == create_user
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class User(object):
    """User class used for mocking AWS backend user objects."""

    def __init__(self, user_name):
        super(User, self).__init__()
        self.access_keys = {}
        self.attached_policies = []
        self.groups = {}
        self.mfa_devices = []
        self.password = None
        self.signing_certs = []
        self.username = user_name


class AWSMock(object):
    """Class for mocking AWS endpoints."""

    def __init__(self):
        """Initialize class."""
        super(AWSMock, self).__init__()
        self.users = {}
        self.groups = {}

    def mock_make_api_call(self, operation_name, kwarg):
        """Entry point for mocking AWS endpoints.

        Calls the mocked AWS operation and returns a parsed
        response.

        If the AWS endpoint is not mocked raise a client error.
        """
        try:
            return getattr(self, inflection(operation_name))(kwarg)
        except AttributeError:
            raise client_error(operation_name, '500', 'Operation not mocked')

    def add_user_to_group(self, kwarg):
        """Add user to the group if group exists."""
        if kwarg[group_name] not in self.groups:
            raise client_error('AddUserToGroup',
                               'Not Found',
                               'Group %s not found' % kwarg[group_name])

        group_id = self.groups[kwarg[group_name]]
        self.users[kwarg[username]].groups[kwarg[group_name]] = group_id
        return user_group_response()

    def create_access_key(self, kwarg):
        """Create access key for user if user exists."""
        if kwarg[username] not in self.users:
            raise client_error('CreateAccessKey',
                               '404',
                               'User %s not found' % kwarg[username])

        key_id = get_random_string(length=20)
        key = get_random_string(length=40)
        self.users[kwarg[username]].access_keys[key_id] = key
        return access_key_response(kwarg[username], key, key_id)

    def create_group(self, kwarg):
        """Create group if it does not exist."""
        if kwarg[group_name] in self.groups:
            raise client_error('CreateGroup',
                               '409',
                               'Group %s exists' % kwarg[group_name])

        group_id = get_random_string(length=10)
        self.groups[kwarg[group_name]] = group_id
        return group_response(kwarg[group_name], group_id)

    def create_login_profile(self, kwarg):
        """Create login profile for user if user has no password."""
        user = self.users[kwarg[username]]
        if user.password:
            raise client_error('CreateLoginProfile',
                               '409',
                               'LoginProfile for %s exists' % user.username)

        user.password = kwarg['Password']
        return login_profile_response(user.username)

    def create_user(self, kwarg):
        """Create user if user does not exist and username is not fake."""
        if kwarg[username] in self.users or kwarg[username] == fake_user_name:
            raise client_error('CreateUser', 'Error', 'User creation failed')

        self.users[kwarg[username]] = User(kwarg[username])
        return user_response(kwarg[username])

    def deactivate_mfa_device(self, kwarg):
        """Deactivate and detach MFA Device from user if device exists."""
        user = self.users[kwarg[username]]
        if kwarg['SerialNumber'] not in user.mfa_devices:
            raise client_error('DeactivateMFADevice',
                               '404',
                               'Device not found')

        user.mfa_devices.remove(kwarg['SerialNumber'])
        return delete_response()

    def delete_access_key(self, kwarg):
        """Delete access key from user if access key exists."""
        access_key = self.users[kwarg[username]].access_keys.pop(
            kwarg['AccessKeyId'], None)
        if not access_key:
            raise client_error('DeleteAccessKey',
                               '404',
                               'Access key not found')

        return delete_response()

    def delete_group(self, kwarg):
        """Delete group if group exists."""
        group = self.groups.pop(kwarg[group_name], None)
        if not group:
            raise client_error('DeleteGroup', '404', 'Group not found')

        return delete_response()

    def delete_login_profile(self, kwarg):
        """Delete login profile (password) from user if users has password."""
        user = self.users[kwarg[username]]
        if not user.password:
            raise client_error('DeleteLoginProfile',
                               '404',
                               'LoginProfile for %s not found' % user.username)

        user.password = None
        return delete_response()

    def delete_signing_certificate(self, kwarg):
        """Delete signing cert if cert exists."""
        user = self.users[kwarg[username]]
        if kwarg['CertificateId'] not in user.signing_certs:
            raise client_error('DeleteSigningCertificate',
                               '404',
                               'Signing certificate not found')

        user.signing_certs.remove(kwarg['CertificateId'])
        return delete_response()

    def delete_user(self, kwarg):
        """Delete user if user exists."""
        if kwarg[username] not in self.users:
            raise client_error('DeleteUser', '404', 'User not found')

        self.users.pop(kwarg[username], None)
        return delete_response()

    def detach_user_policy(self, kwarg):
        """Detach user policy if policy exists."""
        user = self.users[kwarg[username]]
        policy = kwarg['PolicyArn'].split('/')[1]

        if policy not in user.attached_policies:
            raise client_error('DetachUserPolicy',
                               '404',
                               'Attached policy not found')

        user.attached_policies.remove(policy)
        return delete_response()

    def get_user(self, kwarg):
        """Get user if user exists."""
        if kwarg[username] in self.users:
            return user_response(kwarg[username])

        raise client_error('GetUser',
                           'Not Found',
                           'User %s not found' % kwarg[username])

    def list_access_keys(self, kwarg):
        """List all of the users access keys if user exists."""
        if kwarg[username] not in self.users:
            raise client_error('ListAccessKeys', '404', 'User not found')

        keys = self.users[kwarg[username]].access_keys
        return list_access_keys_response(kwarg[username], keys)

    def list_attached_user_policies(self, kwarg):
        """List all of the users attached policies if user exists."""
        if kwarg[username] not in self.users:
            raise client_error('ListAttachedUserPolicies',
                               '404',
                               'User not found')

        policies = self.users[kwarg[username]].attached_policies
        return list_attached_policies_response(policies)

    def list_groups_for_user(self, kwarg):
        """List all of the users groups if user exists."""
        if kwarg[username] not in self.users:
            raise client_error('ListGroupsForUser', '404', 'User not found')

        groups = self.users[kwarg[username]].groups
        return list_user_groups_response(groups)

    def list_mfa_devices(self, kwarg):
        """List all of the users MFA devices if user exists."""
        if kwarg[username] not in self.users:
            raise client_error('ListMFADevices', '404', 'User not found')

        devices = self.users[kwarg[username]].mfa_devices
        return list_mfa_devices_response(kwarg[username], devices)

    def list_signing_certificates(self, kwarg):
        """List all of the users signing certs if the user exists."""
        if kwarg[username] not in self.users:
            raise client_error('ListSigningCertificates',
                               '404',
                               'User not found')

        certs = self.users[kwarg[username]].signing_certs
        return list_signing_certs_response(kwarg[username], certs)

    def remove_user_from_group(self, kwarg):
        """Remove user from group if user exists."""
        if kwarg[username] not in self.users:
            raise client_error('RemoveUserFromGroup', '404', 'User not found')

        self.users[kwarg[username]].groups.pop(kwarg[group_name], None)
        return delete_response()
