#!/usr/bin/env python3
"""Creates and enables cloud trail."""
# -*- coding: utf-8 -*-
#
# Copyright © 2017 SUSE LLC.
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
import json
import random
import string

from contextlib import suppress
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

CHARS = string.ascii_lowercase + string.digits


def get_random_string(length=12):
    """Generate random string of given length with allowed chars."""
    return ''.join(random.choice(CHARS) for index in range(length))


def get_account_id(session):
    """Retrieve principal account id."""
    return session.client('sts').get_caller_identity().get('Account')


def create_bucket(name, policy, session):
    """Create s3 bucket and attach cloudtrail policy."""
    s3 = session.client('s3')

    s3.create_bucket(Bucket=name)
    s3.put_bucket_policy(
        Bucket=name,
        Policy=json.dumps(policy)
    )


def enable_cloud_trail(name, bucket_name, session):
    """Create and enable cloud trail if it does not exist already."""
    cloudtrail = session.client('cloudtrail')

    cloudtrail.create_trail(
        Name=name,
        S3BucketName=bucket_name,
        IncludeGlobalServiceEvents=True,
        IsMultiRegionTrail=True,
        EnableLogFileValidation=True,
    )

    cloudtrail.start_logging(Name=name)


class Command(BaseCommand):
    """Command to create and enable cloud trail in AWS."""

    help = 'Creates a CloudTrail for openbare and enables logging.'

    def handle(self, *args, **options):
        """Create and enable CloudTrail for openbare."""
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        bucket_name = '%s-%s' % ('openbare-cloudtrail', get_random_string())
        policy = {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Sid": "AWSCloudTrailAclCheck20150319",
              "Effect": "Allow",
              "Principal": {"Service": "cloudtrail.amazonaws.com"},
              "Action": "s3:GetBucketAcl",
              "Resource": "arn:aws:s3:::%s" % bucket_name
            },
            {
              "Sid": "AWSCloudTrailWrite20150319",
              "Effect": "Allow",
              "Principal": {"Service": "cloudtrail.amazonaws.com"},
              "Action": "s3:PutObject",
              "Resource": "arn:aws:s3:::%s/AWSLogs/%s/*" % (
                  bucket_name,
                  get_account_id(session)
              ),
              "Condition": {
                  "StringEquals": {
                      "s3:x-amz-acl": "bucket-owner-full-control"
                  }
              }
            }
          ]
        }

        try:
            # Create bucket
            create_bucket(bucket_name, policy, session)
        except Exception as e:
            raise CommandError(
                'Failed to create S3 bucket: %s' % str(e)
            )

        try:
            # Enable cloud trail for all regions
            enable_cloud_trail('OpenbareLogs', bucket_name, session)
        except Exception as e:
            with suppress(Exception):
                # Cleanup bucket if exists
                s3 = session.resource('s3')
                bucket = s3.Bucket(bucket_name)
                for key in bucket.objects.all():
                    key.delete()
                bucket.delete()

            raise CommandError(
                'Failed to create CloudTrail: %s' % str(e)
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'CloudTrail with name: OpenbareLogs created successfully'
                )
            )
