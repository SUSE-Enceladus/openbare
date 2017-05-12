import boto3

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Collect EC2 events from all cloudtrail regions.'

    def handle(self, *args, **options):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        management.call_command(
            'aws_collect',
            *session.get_available_regions('cloudtrail'),
            interactive=False
        )
