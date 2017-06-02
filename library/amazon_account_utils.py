"""Methods used for creating, destroying IAM accounts on AWS."""

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

import boto3
import botocore.exceptions
import collections
import logging
import random

from django.conf import settings

from logging import CRITICAL, ERROR, WARNING, INFO


class AmazonAccountUtils:
    """AWS lendable utils class."""

    logger = logging.getLogger('django')

    def __init__(self, aws_access_key_id, aws_secret_access_key):
        """Initialize access key and secret for AWS account."""
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    def log(self, message, level=logging.DEBUG, depth=0):
        """Prepend string to log messages to denote class."""
        if depth <= 0:
            prefix = 'AmazonAccountUtils: '
        else:
            prefix = "\t" * depth

        if level == CRITICAL:
            self.logger.critical(prefix + str(message))
        elif level == ERROR:
            self.logger.error(prefix + str(message))
        elif level == WARNING:
            self.logger.warning(prefix + str(message))
        elif level == INFO:
            self.logger.info(prefix + str(message))
        else:
            self.logger.debug(prefix + str(message))

    def _make_password(self, length=12):
        """Generate a random password.

        Provides a password of a given length, containing an equal distribution
        of lowercase and uppercase ASCII characters, digits, and puntuation,
        while avoiding ambiguous characters.

        Based on
        http://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_passwords_account-policy.html#password-policy-details
        """
        lowercase = 'abcdefghjkmnopqrstuvwxyz'  # removed ambiguous 'i', 'l'
        uppercase = 'ABCDEFGHJKLMNPQRSTUVWXYZ'  # removed ambiguous 'I', 'O'
        digits = '23456789'  # removed ambiguous '1', '0'
        # removed ambiguous '|', quotes and illegal special characters
        punctuation = '!@#$%^&*()_+-=[]{}'
        password_set = []
        while len(password_set) < length:
            password_set.append(random.choice(lowercase))
            password_set.append(random.choice(uppercase))
            password_set.append(random.choice(digits))
            password_set.append(random.choice(punctuation))
        random.shuffle(password_set)
        return ''.join(password_set)[:length]

    def _get_aws_session(self, region=None):
        self.log('opening session')
        if region:
            return boto3.session.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=region
            )
        return boto3.session.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def _get_ec2_resource(self, region):
        session = self._get_aws_session(region)
        self.log('accessing ec2 resource')
        return session.resource('ec2')

    def _get_iam_resource(self, session=None):
        if not session:
            session = self._get_aws_session()
        self.log('accessing IAM resource')
        return session.resource('iam')

    def _get_iam_user(self, username):
        resource = self._get_iam_resource()
        user = resource.User(username)
        try:
            user.load()
        except botocore.exceptions.ClientError:
            self.log(
                "user '%s' does not exist" % username,
                WARNING
             )
            return None
        else:
            self.log("user '%s' found" % username)
            return user

    def _cleanup_iam_user(self, iam_user):
        """Cleanup resources for IAM user.

        In order to delete an IAM user, the user must not belong to any groups,
        have any keys or signing certificates, or have any attached policies.
        """
        self.log("cleaning up user '%s'" % iam_user.user_name, INFO)
        self.log(
            "deleting login profile for user '%s'" % iam_user.user_name,
            depth=1
        )

        # First, delete the login profile, so the user can't be logged in
        # while we are cleaning up. Then roll through the rest of the dependent
        # resources.
        try:
            iam_user.LoginProfile().delete()
        except botocore.exceptions.ClientError as e:
            self.log(e, ERROR)
        for access_key in iam_user.access_keys.all():
            self.log(
                "deleting access key %s" % (access_key.access_key_id),
                depth=1
            )
            access_key.delete()
        for mfa_device in iam_user.mfa_devices.all():
            self.log(
                "disassociating mfa device '%s' from user '%s'" %
                (mfa_device.serial_number, iam_user.user_name),
                depth=1
            )
            mfa_device.disassociate()
        for signing_certificate in iam_user.signing_certificates.all():
            self.log(
                "deleting signing certificate %s" %
                signing_certificate.certificate_id,
                depth=1
            )
            signing_certificate.delete()
        for group in iam_user.groups.all():
            self.log(
                "removing user '%s' from group '%s'" %
                (iam_user.user_name, group.name),
                depth=1
            )
            iam_user.remove_group(GroupName=group.name)
        for attached_policy in iam_user.attached_policies.all():
            self.log(
                "detaching policy '%s' from user '%s'" %
                (attached_policy.policy_name, iam_user.user_name),
                depth=1
            )
            iam_user.detach_policy(PolicyArn=attached_policy.arn)
        return True

    def iam_user_exists(self, username):
        """Return true if account exists."""
        return True if self._get_iam_user(username) else False

    def create_iam_account(self, username, group=None):
        """Create an IAM account for the given username.

        Returns:
            The required credentials.
        """
        self.log("creating IAM user '%s'" % username, INFO)

        alias = getattr(settings, 'AWS_ACCOUNT_ID_ALIAS', None)
        if alias:
            url = 'https://{}.signin.aws.amazon.com/console'.format(alias)
        else:
            url = 'https://signin.aws.amazon.com/console'

        credentials = collections.OrderedDict([
            ('Web Console URL', url),
            ('Username', username),
            ('Password', self._make_password())
        ])
        iam_resource = self._get_iam_resource()
        iam_user = iam_resource.User(username).create(Path='/openbare/')
        try:
            if group:
                iam_user.add_group(GroupName=group)
            iam_user.create_login_profile(
                Password=credentials['Password'],
                PasswordResetRequired=False
            )
            access_key_pair = iam_user.create_access_key_pair()
        except Exception as e:
            self._cleanup_iam_user(iam_user)
            iam_user.delete()
            raise
        credentials.update([
            ('Access Key ID', access_key_pair.access_key_id),
            ('Secret Access Key', access_key_pair.secret_access_key)
        ])
        return credentials

    def destroy_iam_account(self, username):
        """Cleanup and delete IAM user account."""
        self.log("destroying IAM user '%s'" % username, INFO)
        iam_user = self._get_iam_user(username)
        if iam_user:
            self._cleanup_iam_user(iam_user)
            iam_user.delete()
            return True
        else:
            return False

    def cleanup_resources(self, lendable):
        resources = collections.defaultdict(list)
        for resource in lendable.resources.all():
            resources[resource.scope].append(resource)

        for region, resource_list in resources.items():
            ec2 = self._get_ec2_resource(region)
            for resource in resource_list:
                if resource.type == 'library.awsinstance':
                    inst = ec2.Instance(resource.resource_id)
                    try:
                        inst.state
                    except AttributeError:
                        self.log(
                            'Instance %s not found' % inst.id,
                            INFO
                        )
                    else:
                        if resource.preserve:
                            self.log(
                                'Instance %s preserved' % inst.id,
                                INFO
                            )
                            resource.lendable = None
                            resource.save()
                        elif resource.released:
                            self.log(
                                'Instance %s already released' % inst.id,
                                INFO
                            )
                        else:
                            inst.terminate()
                            self.log(
                                'Instance %s terminated' % inst.id,
                                INFO
                            )
                            resource.reaped = True
                            resource.save()
