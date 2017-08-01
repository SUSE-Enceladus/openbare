#!/usr/bin/env python3
"""AWS EC2 event collection script."""
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
import logging

from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import UTC
from library.models import (
    AmazonDemoAccount,
    AWSInstance,
    AWSResource,
    ManagementCommand
)

EVENTS = {
    'CreateTags': AWSResource,
    'DeleteTags': AWSResource,
    'RunInstances': AWSInstance,
    'TerminateInstances': AWSInstance
}
MAX_RESULTS = 50
MODULE_NAME = __name__.split('.')[-1]


class Command(BaseCommand):
    help = 'Collect EC2 events from cloudtrail region.'
    logger = logging.getLogger(MODULE_NAME)

    def add_arguments(self, parser):
        parser.add_argument('region', nargs='+')

    def handle(self, *args, **options):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        for region in options['region']:
            self.logger.debug(
                'Collecting EC2 resources in region: %s' % region
            )

            current_time = datetime.now(UTC())
            name = ''.join([MODULE_NAME, '_', region])
            try:
                command, created = ManagementCommand.objects.get_or_create(
                    name=name
                )

                if command.last_success:
                    start_time = command.last_success - timedelta(hours=1)
                else:
                    start_time = current_time - timedelta(days=7)

                cloud_trail = session.client(
                    'cloudtrail',
                    region_name=region
                )

                token = None
                events = []
                while True:
                    if token:
                        response = cloud_trail.lookup_events(
                            StartTime=start_time,
                            MaxResults=MAX_RESULTS,
                            NextToken=token
                        )
                    else:
                        response = cloud_trail.lookup_events(
                            StartTime=start_time,
                            MaxResults=MAX_RESULTS
                        )
                    events += response['Events']

                    try:
                        token = response['NextToken']
                    except KeyError:
                        break

                # Events are stacked lifo so reverse to process
                # the events in order of occurrence.
                events.reverse()
                for event in events:
                    if event['EventName'] in EVENTS:
                        detail = json.loads(event['CloudTrailEvent'])
                        principal = detail['userIdentity']['principalId']
                        user_type = detail['userIdentity']['type']

                        if user_type == 'IAMUser':
                            user = detail['userIdentity']['userName']
                        elif user_type == 'Root':
                            user = principal
                        else:
                            continue

                        if 'errorCode' not in detail:
                            self.handle_event(detail, event, user)

            except Exception as error:
                self.logger.error(
                    'An error occurred parsing cloudtrail events for region'
                    ' %s: %s' % (region, error)
                )
            else:
                command.last_success = current_time
                command.save()

    def handle_event(self, detail, event, user):
        try:
            lendable = AmazonDemoAccount.lendables.get(username=user)
        except:
            lendable = None

        result = EVENTS[event['EventName']].parse_event(
            detail,
            event,
            lendable
        )

        msg = 'Processed event %s for id(s): %s' % (
            event['EventName'],
            result
        )

        self.logger.debug(
            msg
        )
