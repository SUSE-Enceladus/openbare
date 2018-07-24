""""Mocked responses for AWS endpoints."""

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

from botocore.exceptions import ClientError
from datetime import datetime
from django.utils.timezone import utc

from .constants import signing_cert


def client_error(operation, code, message):
    """Return botocore client error instance."""
    parsed_response = {'Error': {'Code': code, 'Message': message}}
    return ClientError(parsed_response, operation)


def get_time_now():
    """Return the time as a datetime object and string."""
    now = datetime.now(utc)
    now_str = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return now, now_str


def response_metadata(now_str):
    """Return the default metadata response."""
    metadata = {
        'ResponseMetadata':
            {'RequestId': '2614a68d-ada7-11e6-8c37-b3baab09bf37',
             'HTTPStatusCode': 200,
             'RetryAttempts': 0,
             'HTTPHeaders':
                 {'content-length': '450',
                  'content-type': 'text/xml',
                  'date': now_str,
                  'x-amzn-requestid': '2614a68d-ada7-11e6-8c37-b3baab09bf37'
                  }
             }
    }
    return metadata


def access_key_response(username, key, key_id):
    """Response for create/get access key."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['AccessKey'] = {
        'CreateDate': now,
        'Status': 'Active',
        'AccessKeyId': key_id,
        'UserName': username,
        'SecretAccessKey': key
    }
    return parsed_response


def delete_response():
    """Generic response for deletion endpoints."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    return parsed_response


def group_response(group_name, group_id):
    """Response for create/get group."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['Group'] = {
        'GroupId': group_id,
        'GroupName': group_name,
        'Arn': 'arn:aws:iam::123456789123:group/%s' % group_name,
        'Path': '/openbare/'
    }
    return parsed_response


def list_access_keys_response(username, keys):
    """Response for list user access keys endpoint."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    keys_response = [{'CreateDate': now,
                      'Status': 'Active',
                      'AccessKeyId': key,
                      'UserName': username} for key, val in keys.items()]
    parsed_response['AccessKeyMetadata'] = keys_response
    return parsed_response


def list_attached_policies_response(policies):
    """Response for list user attached policies endpoint."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    policies_response = [{'PolicyArn': 'arn:aws:iam::aws:policy/%s' % policy,
                          'PolicyName': policy} for policy in policies]
    parsed_response['AttachedPolicies'] = policies_response
    return parsed_response


def list_mfa_devices_response(username, devices):
    """Response for list user MFA Devices endpoint."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    devices_response = [{'SerialNumber': device,
                         'UserName': username} for device in devices]
    parsed_response['MFADevices'] = devices_response
    return parsed_response


def list_signing_certs_response(username, certs):
    """Response for list user signing certificates."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    certs_response = [{'UserName': username,
                       'CertificateId': cert,
                       'CertificateBody': signing_cert} for cert in certs]
    parsed_response['Certificates'] = certs_response
    return parsed_response


def list_user_groups_response(groups):
    """Response for list user groups."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['IsTruncated'] = False
    groups_response = [{'Path': '/openbare/',
                        'Arn': 'arn:aws:iam::123456789012:group/%s' % key,
                        'GroupName': key,
                        'GroupId': val} for key, val in groups.items()]
    parsed_response['Groups'] = groups_response
    return parsed_response


def login_profile_response(username):
    """Response for list user login profiles."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['LoginProfile'] = {
        'CreateDate': now,
        'PasswordResetRequired': False,
        'UserName': username
    }
    return parsed_response


def user_response(username):
    """Response for create/get user."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    parsed_response['User'] = {
        'UserId': 'AIDAJKBPJ3KLDYBUV64DE',
        'CreateDate': now,
        'UserName': username,
        'Arn': 'arn:aws:iam::123456789123:user/openbare/%s' % username,
        'Path': '/openbare/'
    }
    return parsed_response


def user_group_response():
    """Response for add user to group."""
    now, now_str = get_time_now()
    parsed_response = response_metadata(now_str)
    return parsed_response
