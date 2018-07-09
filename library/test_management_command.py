from datetime import datetime
from django.test import TestCase
from django.utils.timezone import UTC

from library.models import ManagementCommand


class ManagementCommandTestCase(TestCase):
    """Test management command model in library app."""

    def setUp(self):
        pass

    def test_create_command(self):
        name = 'test_command'
        command, created = ManagementCommand.objects.get_or_create(
            name=name
        )

        self.assertEqual(command.name, name)
        self.assertEqual(command.last_success, None)
        self.assertTrue(created)

        current_time = datetime.now(UTC())
        command.last_success = current_time
        command.save()

        command, created = ManagementCommand.objects.get_or_create(
            name=name
        )
        self.assertFalse(created)
        self.assertNotEqual(command.last_success, None)
