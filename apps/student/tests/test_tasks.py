from datetime import date

from freezegun import freeze_time

from django import test
from django.db import connection

from apps.module.tests.factories import ModuleFactory

from .. import models, tasks
from . import factories


class TestUpdateFormattedAddresses(test.TestCase):
    def test_updating(self):
        student = factories.StudentFactory()
        # Raw sql command to create an address record without `formatted`, as though inserted by SSIS
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO address (line1, student, type, is_default, is_billing) VALUES (%s, %s, %s, %s, %s)",
                ['Rewley House', student.pk, 200, True, False],
            )

        result = tasks.update_formatted_addresses()

        self.assertEqual(result, 1)
        address = models.Address.objects.first()
        self.assertEqual(address.formatted, "Rewley House")


@freeze_time(date(2020, 1, 1))
class TestRemoveEnquiries(test.TestCase):
    def test_date_cutoff(self):
        student = factories.StudentFactory()
        module = ModuleFactory()
        old = models.Enquiry.objects.create(created_on=date(2000, 1, 1), student=student, module=module)
        new = models.Enquiry.objects.create(created_on=date(2019, 1, 1), student=student, module=module)

        tasks.remove_old_enquiries(years=3, months=0)

        self.assertEqual(models.Enquiry.objects.first(), new)

        with self.assertRaises(models.Enquiry.DoesNotExist):
            old.refresh_from_db()
