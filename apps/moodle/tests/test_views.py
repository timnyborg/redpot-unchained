from django.test import TestCase
from django.urls import reverse

import apps.moodle
from apps.core.utils.tests import LoggedInMixin
from apps.enrolment.tests.factories import EnrolmentFactory

from .. import models
from . import factories


class TestViews(LoggedInMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.MOODLE_ID = 8902567
        cls.student = factories.StudentFactory()

    def test_moodle_id(self):
        response = self.client.post(
            reverse('moodle:new', kwargs={'student_id': self.student.id}),
            data={'student': self.student.pk, 'moodle_id': self.MOODLE_ID, 'first_module_code': 123},
        )
        self.assertEqual(response.status_code, 302)
        moodle_id = models.MoodleID.objects.last()
        self.assertEqual(moodle_id.student_id, self.student.id)

    def test_edit_moodle_id(self):
        self.moodle = apps.moodle.tests.factories.MoodleFactory(student=self.student)
        self.client.post(reverse('moodle:edit', kwargs={'pk': self.moodle.id}), {'moodle_id': 876987987})
        self.moodle.refresh_from_db()
        self.assertEqual(self.moodle.moodle_id, 876987987)

    def test_delete_moodle_id(self):
        self.moodle = apps.moodle.tests.factories.MoodleFactory(student=self.student, moodle_id=self.MOODLE_ID)
        self.assertEqual(self.moodle.moodle_id, self.MOODLE_ID)
        self.client.post(reverse('moodle:delete', kwargs={'pk': self.moodle.pk}))
        with self.assertRaises(models.MoodleID.DoesNotExist):
            self.moodle.refresh_from_db()


class TestAssignView(LoggedInMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.enrolment = EnrolmentFactory()
        cls.url = reverse('moodle:assign', args=[cls.enrolment.module.pk])

    def test_student_list(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        # Check that a moodle record has been created with the right details
        moodle_record = self.enrolment.qa.student.moodle_id
        self.assertEqual(moodle_record.first_module_code, self.enrolment.module.code)
        self.assertEqual(moodle_record.created_by, self.user.username)
