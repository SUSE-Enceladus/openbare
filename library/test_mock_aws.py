""""Tests for mocked AWS endpoints."""

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

from botocore.exceptions import ClientError
from django.test import TestCase

from library.mock_aws.aws_endpoints import AWSMock
from library.mock_aws.constants import group_name, username


class AWSMockTestCase(TestCase):
    """Test AWSMock class."""

    def setUp(self):
        """Setup test case."""
        self.mocker = AWSMock()
        self.kwarg = {username: 'John',
                      group_name: 'Admins'}

    def test_unmocked_operation(self):
        """Test operation not mocked error is returned."""
        msg = 'An error occurred (500) when calling the CreateGecko ' \
              'operation: Operation not mocked'

        try:
            self.mocker.mock_make_api_call('CreateGecko',
                                           {'Name': 'gecko'})
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_get_user_exception(self):
        """Test get non existent user raises exception."""
        msg = 'An error occurred (Not Found) when calling the GetUser' \
              ' operation: User John not found'

        try:
            # Assert get non existing user exception
            self.mocker.get_user(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_list_user_groups_exception(self):
        """Test list non existent user groups raises exception."""
        msg = 'An error occurred (404) when calling the ' \
              'ListGroupsForUser operation: User John not found'

        try:
            # Assert list non existent user groups exception
            self.mocker.list_groups_for_user(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_add_user_group_exception(self):
        """Test add user to non existent group raises exception."""
        msg = 'An error occurred (Not Found) when calling the AddUserToGroup' \
              ' operation: Group Admins not found'

        try:
            # Assert add user to non existing group exception
            self.mocker.add_user_to_group(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_user_group(self):
        """Test user and group endpoints."""
        # Create user and group and add user to group
        self.mocker.create_user(self.kwarg)
        self.mocker.create_group(self.kwarg)
        self.mocker.add_user_to_group(self.kwarg)

        # Assert user and group exist and assert user in group
        self.assertIn(self.kwarg[username], self.mocker.users)
        self.assertIn(self.kwarg[group_name], self.mocker.groups)
        self.assertIn(self.kwarg[group_name],
                      self.mocker.users[self.kwarg[username]].groups)

        msg = 'An error occurred (409) when calling the CreateGroup' \
              ' operation: Group Admins exists'

        try:
            # Assert create group exists raises exception
            self.mocker.create_group(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

        msg = 'An error occurred (409) when calling the CreateUser' \
              ' operation: User John exists'

        try:
            # Assert create user exists raises exception
            self.mocker.create_user(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

        # Get user response
        response = self.mocker.get_user(self.kwarg)
        self.assertEqual(response['User'][username], self.kwarg[username])

        # List groups for user response
        response = self.mocker.list_groups_for_user(self.kwarg)
        self.assertEqual(response['Groups'][0][group_name],
                         self.kwarg[group_name])
        self.assertEqual(1, len(response['Groups']))

        # Remove user from group
        self.mocker.remove_user_from_group(self.kwarg)
        self.assertNotIn(self.kwarg[group_name],
                         self.mocker.users[self.kwarg[username]].groups)

        # Delete group
        self.mocker.delete_group(self.kwarg)
        self.assertNotIn(self.kwarg[group_name], self.mocker.groups)

        # Delete user
        self.mocker.delete_user(self.kwarg)
        self.assertNotIn(self.kwarg[username], self.mocker.users)

    def test_delete_user_exception(self):
        """Test delete non existent user raises exception."""
        msg = 'An error occurred (404) when calling the DeleteUser' \
              ' operation: User not found'

        try:
            # Assert delete non existent user exception
            self.mocker.delete_user(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_delete_group_exception(self):
        """Test delete non existent group raises exception."""
        msg = 'An error occurred (404) when calling the DeleteGroup' \
              ' operation: Group Admins not found'

        try:
            # Assert delete non existent user exception
            self.mocker.delete_group(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_remove_user_group_exception(self):
        """Test remove non existent user from group raises exception."""
        msg = 'An error occurred (404) when calling the RemoveUserFromGroup' \
              ' operation: User John not found'

        try:
            # Assert remove non existent user from group exception
            self.mocker.remove_user_from_group(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_create_access_key_exception(self):
        """Test create access key for non existent user raises exception."""
        msg = 'An error occurred (404) when calling the CreateAccessKey' \
              ' operation: User John not found'

        try:
            # Assert create access key for non existent user exception
            self.mocker.create_access_key(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_delete_access_key_exception(self):
        """Test delete non existent access key raises exception."""
        msg = 'An error occurred (404) when calling the DeleteAccessKey' \
              ' operation: Access key not found'

        self.mocker.create_user(self.kwarg)
        self.kwarg['AccessKeyId'] = 'key213'

        try:
            # Assert delete non existent access key exception
            self.mocker.delete_access_key(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_list_access_key_exception(self):
        """Test list access keys for non existent user raises exception."""
        msg = 'An error occurred (404) when calling the ListAccessKeys' \
              ' operation: User John not found'

        try:
            # Assert list access keys for non existent user exception
            self.mocker.list_access_keys(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_access_key(self):
        """Test access key endpoints."""
        self.mocker.create_user(self.kwarg)
        response = self.mocker.create_access_key(self.kwarg)

        # Get created key id
        key_id = response['AccessKey']['AccessKeyId']

        # Get user access keys
        response = self.mocker.list_access_keys(self.kwarg)

        # Assert id's are equal and keys length is 1
        self.assertEqual(key_id,
                         response['AccessKeyMetadata'][0]['AccessKeyId'])
        self.assertEqual(1, len(response['AccessKeyMetadata']))

        # Delete access key
        self.kwarg['AccessKeyId'] = key_id
        self.mocker.delete_access_key(self.kwarg)

        # Confirm deletion
        self.assertEqual(0, len(
            self.mocker.users[self.kwarg[username]].access_keys))

    def test_create_login_profile_exception(self):
        """Test create login profile already exists raises exception."""
        msg = 'An error occurred (409) when calling the CreateLoginProfile' \
              ' operation: LoginProfile for John exists'

        # Create login profile
        self.mocker.create_user(self.kwarg)
        self.kwarg['Password'] = 'password'
        self.mocker.create_login_profile(self.kwarg)

        try:
            # Assert create login profile already exists exception
            self.mocker.create_login_profile(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_delete_login_profile_exception(self):
        """Test delete non existent login profile raises exception."""
        msg = 'An error occurred (404) when calling the DeleteLoginProfile' \
              ' operation: LoginProfile for John not found'

        self.mocker.create_user(self.kwarg)

        try:
            # Assert delete non existent login profile exception
            self.mocker.delete_login_profile(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_login_profile(self):
        """Test login profile endpoints."""
        self.mocker.create_user(self.kwarg)

        # Create login profile
        self.kwarg['Password'] = 'password'
        response = self.mocker.create_login_profile(self.kwarg)
        self.assertEqual(self.kwarg[username],
                         response['LoginProfile'][username])
        self.assertEqual('password',
                         self.mocker.users[self.kwarg[username]].password)

        # Delete profile
        self.mocker.delete_login_profile(self.kwarg)
        self.assertEqual(None,
                         self.mocker.users[self.kwarg[username]].password)

    def test_deactivate_mfa_device_exception(self):
        """Test deactivate non existent mfa device raises exception."""
        msg = 'An error occurred (404) when calling the DeactivateMFADevice' \
              ' operation: Device not found'

        self.mocker.create_user(self.kwarg)
        self.kwarg['SerialNumber'] = '44324234213'

        try:
            # Assert deactivate non existent mfa device exception
            self.mocker.deactivate_mfa_device(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_list_mfa_device_exception(self):
        """Test list mfa devices for non existent user raises exception."""
        msg = 'An error occurred (404) when calling the ListMFADevices' \
              ' operation: User John not found'

        try:
            # Assert list mfa devices for non existent user exception
            self.mocker.list_mfa_devices(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_mfa_device(self):
        """Test mfa device endpoints."""
        self.mocker.create_user(self.kwarg)

        # Add mfa device
        self.mocker.users['John'].mfa_devices.append('44324234213')

        # Lists mfa devices
        response = self.mocker.list_mfa_devices(self.kwarg)

        self.assertEqual('44324234213',
                         response['MFADevices'][0]['SerialNumber'])
        self.assertEqual(1, len(response['MFADevices']))

        # Deactivate mfa device
        self.kwarg['SerialNumber'] = '44324234213'
        self.mocker.deactivate_mfa_device(self.kwarg)

        # Confirm deactivation
        self.assertEqual(0, len(self.mocker.users['John'].mfa_devices))

    def test_delete_signing_cert_exception(self):
        """Test delete non existent signing cert raises exception."""
        msg = 'An error occurred (404) when calling the ' \
              'DeleteSigningCertificate operation: Signing certificate' \
              ' not found'

        self.mocker.create_user(self.kwarg)
        self.kwarg['CertificateId'] = '44324234213'

        try:
            # Assert delete non existent signing certificate exception
            self.mocker.delete_signing_certificate(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_list_signing_certificates_exception(self):
        """Test list signing certs for non existent user raises exception."""
        msg = 'An error occurred (404) when calling the ' \
              'ListSigningCertificates operation: User John not found'

        try:
            # Assert list signing certs for non existent user exception
            self.mocker.list_signing_certificates(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_signing_certificate(self):
        """Test signing certificate endpoints."""
        self.mocker.create_user(self.kwarg)

        # Add signing cert
        self.mocker.users['John'].signing_certs.append('44324234213')

        # Lists mfa devices
        response = self.mocker.list_signing_certificates(self.kwarg)

        self.assertEqual('44324234213',
                         response['Certificates'][0]['CertificateId'])
        self.assertEqual(1, len(response['Certificates']))

        # Delete signing cert
        self.kwarg['CertificateId'] = '44324234213'
        self.mocker.delete_signing_certificate(self.kwarg)

        # Confirm deletion
        self.assertEqual(0, len(self.mocker.users['John'].signing_certs))

    def test_detach_user_policy_exception(self):
        """Test detach non existent user policy raises exception."""
        msg = 'An error occurred (404) when calling the ' \
              'DetachUserPolicy operation: Attached policy not found'

        self.mocker.create_user(self.kwarg)
        self.kwarg['PolicyArn'] = 'arn:aws:iam::aws:policy/Admins'

        try:
            # Assert detach non existent user policy exception
            self.mocker.detach_user_policy(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_list_attached_user_policies_exception(self):
        """Test list user policies for non existent user raises exception."""
        msg = 'An error occurred (404) when calling the ' \
              'ListAttachedUserPolicies operation: User John not found'

        try:
            # Assert list user policies for non existent user exception
            self.mocker.list_attached_user_policies(self.kwarg)
        except ClientError as e:
            self.assertEqual(msg, str(e))

    def test_user_policy(self):
        """Test user policy endpoints."""
        self.mocker.create_user(self.kwarg)

        # Attach user policy
        self.mocker.users['John'].attached_policies.append('Admins')

        # Lists attached user policies
        response = self.mocker.list_attached_user_policies(self.kwarg)

        self.assertEqual('Admins',
                         response['AttachedPolicies'][0]['PolicyName'])
        self.assertEqual(1, len(response['AttachedPolicies']))

        # Detach attached policy
        self.kwarg['PolicyArn'] = 'arn:aws:iam::aws:policy/Admins'
        self.mocker.detach_user_policy(self.kwarg)

        # Confirm policy detached
        self.assertEqual(0, len(self.mocker.users['John'].attached_policies))
