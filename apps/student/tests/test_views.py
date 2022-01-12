from datetime import datetime
from unittest.mock import patch
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.qualification_aim.tests.factories import QualificationAimFactory
from apps.tutor.models import Tutor
from apps.tutor.tests.factories import TutorFactory, TutorModuleFactory

from .. import models, services
from . import factories


class TestViewsWithoutLogin(TestCase):
    def test_views_require_login(self):
        response = self.client.get(reverse('student:search'))
        self.assertEqual(response.status_code, 302)


class TestSearch(TestCase):
    url = reverse('student:search')

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory(
            firstname='Stephen',
            nickname='Steve',
        )
        cls.student.emails.create(email='steve@smith.net')
        cls.student.addresses.create(postcode='OX1 2JA')

    def setUp(self):
        self.client.force_login(self.user)

    def test_search_by_nickname(self):
        response = self.client.get(self.url, data={'firstname': 'Steve'})
        self.assertEqual(len(response.context['table'].rows), 1)
        response = self.client.get(self.url, data={'firstname': 'Todd'})
        self.assertEqual(len(response.context['table'].rows), 0)

    def test_search_by_full_email(self):
        response = self.client.get(self.url, data={'email': 'steve@smith.net'})
        self.assertEqual(len(response.context['table'].rows), 1)
        response = self.client.get(self.url, data={'email': 'todd@smith.net'})
        self.assertEqual(len(response.context['table'].rows), 0)

    def test_search_by_partial_email(self):
        response = self.client.get(self.url, data={'email': '@smith.net'})
        self.assertEqual(len(response.context['table'].rows), 1)

    def test_search_by_postcode(self):
        response = self.client.get(self.url, data={'postcode': 'OX1 2JA'})
        self.assertEqual(len(response.context['table'].rows), 1)
        response = self.client.get(self.url, data={'postcode': 'TE1 1ST'})
        self.assertEqual(len(response.context['table'].rows), 0)


class TestCreateStudent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory()
        cls.url = reverse('student:new')

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_create_student(self):
        # Do the search, loading the session
        response = self.client.post(
            self.url,
            data={
                'surname': 'smith',
                'firstname': 'steve',
                'email': 'test@test.net',
            },
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            self.url,
            data={'action': 'create'},
        )
        self.assertEqual(response.status_code, 302)
        newest_student = models.Student.objects.last()
        self.assertEqual(newest_student.surname, 'smith')
        self.assertEqual(newest_student.emails.first().email, 'test@test.net')


class TestCreateEmail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory()
        cls.url = reverse('student:email:new', kwargs={'student_id': cls.student.pk})
        cls.invalid_url = reverse('student:email:new', kwargs={'student_id': 0})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_creates_email(self):
        response = self.client.post(
            self.url,
            data={
                'student': self.student.pk,
                'email': 'test@test.net',
                'note': 'An email address!',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.student.emails.first().email, 'test@test.net')

    def test_invalid_student_returns_404(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 404)


class TestEmailsViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory()
        cls.email = factories.EmailFactory(student=cls.student)

    def setUp(self):
        self.client.force_login(self.user)

    def test_edit_email(self):
        self.client.post(reverse('student:email:edit', kwargs={'pk': self.email.pk}), {'email': 'email1@test.com'})
        self.email.refresh_from_db()
        self.assertEqual(self.email.email, 'email1@test.com')

    def test_delete_email(self):
        new_email = factories.EmailFactory(student=self.student)
        self.assertEqual(self.email.student, new_email.student)
        self.assertEqual(self.student.emails.count(), 2)
        self.client.post(reverse('student:email:delete', kwargs={'pk': self.email.pk}))
        self.student.refresh_from_db()
        self.assertEqual(self.student.emails.count(), 1)


class TestMakeTutor(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory()
        cls.url = reverse('student:make-tutor', kwargs={'student_id': cls.student.pk})

    def setUp(self):
        self.client.force_login(self.user)

    def test_make_tutor(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.student.refresh_from_db()
        self.assertEqual(Tutor.objects.last().student, self.student)


class TestStudentDetailsView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory()
        cls.url = reverse('student:view', args=[cls.student.pk])

    def setUp(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TestStudentIsATutor(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory()
        cls.student_tutor = TutorFactory(student=cls.student)
        cls.url = reverse('student:view', args=[cls.student.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_student_is_tutor(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['tutor'].student.id, self.student.pk)


class TestStudentIsNotATutor(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory()
        cls.url = reverse('student:view', args=[cls.student.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_student_is_tutor(self):
        response = self.client.get(self.url)
        self.assertIsNone(response.context['tutor'])


class TestStudentModuleTutor(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.tutor_on_module = TutorModuleFactory()
        cls.url = reverse('student:view', args=[cls.tutor_on_module.tutor.student.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_student(self):
        response = self.client.get(self.url)
        self.assertEqual(self.tutor_on_module.module.id, response.context['tutor_modules'].first().module.id)
        self.assertEqual(self.tutor_on_module.tutor.id, response.context['tutor_modules'].first().tutor.id)


class TestStudentTutorModules(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.profiles = []
        cls.profiles.extend(TutorModuleFactory.create_batch(1, role="Speaker"))
        cls.profiles.extend(TutorModuleFactory.create_batch(4, tutor=cls.profiles[0].tutor, role="Speaker"))
        cls.profiles.extend(TutorModuleFactory.create_batch(3, tutor=cls.profiles[0].tutor, role="Tutor"))
        cls.url = reverse('student:view', args=[cls.profiles[0].tutor.student.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_total_unfiltered_tutor_modules_count(self):
        response = self.client.get(self.url)
        # Test unfiltered courses match
        self.assertCountEqual(self.profiles, response.context['tutor_modules'])
        self.assertNotEqual(self.profiles, response.context['tutor_modules_query'])

    def test_total_filtered_tutor_modules_count(self):
        response = self.client.get(self.url + '?tutor_role=Tutor')
        # Test filtered courses match
        self.assertCountEqual(self.profiles, response.context['tutor_modules'])
        self.assertEqual(response.context['tutor_modules_query'].count(), 3)
        self.assertIsNotNone(response.context['tutor_module_role'])


class TestStudentEnrolment(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.qa = QualificationAimFactory()
        cls.url = reverse('student:view', args=[cls.qa.student.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_student_enrolment(self):
        response = self.client.get(self.url)
        self.assertIsNotNone(response.context['qa_list'])
        self.assertEquals(response.context['qa_list'][0].programme.qualification.id, 1)
        self.assertTrue(response.context['qa_list'][0].non_accredited)


class TestCreateAddress(LoggedInViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.student = factories.StudentFactory()
        cls.url = reverse('student:address:new', kwargs={'student_id': cls.student.id})

    def test_create(self):
        response = self.client.post(
            self.url, data={'line1': 'Place', 'type': models.Address.Types.PERMANENT, 'country': 'Canada'}
        )
        self.assertEqual(response.status_code, 302)
        address = models.Address.objects.last()
        self.assertEqual(address.student_id, self.student.id)


class TestMoodleIdViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.MOODLE_ID = 8902567
        cls.student = factories.StudentFactory()
        cls.url = reverse('student:moodle-id:new', kwargs={'student_id': cls.student.id})

    def setUp(self):
        self.client.force_login(self.user)

    def test_moodle_id(self):
        response = self.client.post(
            self.url, data={'student': self.student.pk, 'moodle_id': self.MOODLE_ID, 'first_module_code': 123}
        )
        self.assertEqual(response.status_code, 302)
        moodle_id = models.MoodleID.objects.last()
        self.assertEqual(moodle_id.student_id, self.student.id)

    def test_edit_moodle_id(self):
        self.moodle = factories.MoodleFactory(student=self.student)
        self.client.post(reverse('student:moodle-id:edit', kwargs={'pk': self.moodle.id}), {'moodle_id': 876987987})
        self.moodle.refresh_from_db()
        self.assertEqual(self.moodle.moodle_id, 876987987)

    def test_delete_moodle_id(self):
        self.moodle = factories.MoodleFactory(student=self.student, moodle_id=self.MOODLE_ID)
        self.assertEqual(self.moodle.moodle_id, self.MOODLE_ID)
        self.client.post(reverse('student:moodle-id:delete', kwargs={'pk': self.moodle.pk}))
        with self.assertRaises(models.MoodleID.DoesNotExist):
            self.moodle.refresh_from_db()


class TestPhone(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory()
        cls.url = reverse('student:phone:new', kwargs={'student_id': cls.student.pk})
        cls.invalid_url = reverse('student:phone:new', kwargs={'student_id': 0})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_creates_phone(self):
        response = self.client.post(
            self.url,
            data={
                'student': self.student.pk,
                'number': '+(44) 1865 245252',
                'type': models.Phone.PhoneTypeChoices.PHONE,
                'is_default': True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.student.phones.first().number, '+(44) 1865 245252')
        self.assertTrue(self.student.phones.first().is_default)

    def test_edit_phone(self):
        self.phone = factories.PhoneFactory(student=self.student)
        response = self.client.post(
            reverse('student:phone:edit', kwargs={'pk': self.phone.pk}),
            data={'number': '+(92) 1675 2445252', 'type': models.Phone.PhoneTypeChoices.FAX},
        )
        self.phone.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.phone.number, '+(92) 1675 2445252')

    def test_invalid_student_phone_returns_404(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 404)


class TestOtherID(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory()
        cls.url = reverse('student:other-id:new', kwargs={'student_id': cls.student.pk})
        cls.invalid_url = reverse('student:other-id:new', kwargs={'student_id': 0})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_creates_other_id(self):
        response = self.client.post(
            self.url,
            data={
                'student': self.student.pk,
                'number': '2345678998765',
                'type': models.OtherID.OtherIdTypeChoices.STUDENT_SUPPORT_NUM,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.student.other_ids.first().number, '2345678998765')
        self.assertEqual(
            self.student.other_ids.first().type, models.OtherID.OtherIdTypeChoices.STUDENT_SUPPORT_NUM.value
        )

    def test_edit_other_id(self):
        self.other_id = factories.OtherIDFactory(student=self.student)
        response = self.client.post(
            reverse('student:other-id:edit', kwargs={'pk': self.other_id.pk}),
            {'number': '2345678998765', 'type': models.OtherID.OtherIdTypeChoices.VISA_ID},
        )
        self.other_id.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.other_id.number, '2345678998765')
        self.assertEqual(self.student.other_ids.first().type, models.OtherID.OtherIdTypeChoices.VISA_ID)

    def test_invalid_student_other_id_returns_404(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 404)


class TestEditStudent(LoggedInViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.student = factories.StudentFactory(sits_id=None)
        cls.url = cls.student.get_edit_url()

    def test_sits_lock(self):
        self.student.sits_id = 1
        self.student.save()
        response = self.client.get(self.get_url())
        self.assertTrue(response.context['form'].fields['surname'].disabled)

    def test_post(self):
        response = self.client.post(
            self.get_url(),
            data={
                'surname': 'newsurname',
                # Unchanged values
                'firstname': self.student.firstname,
                'nationality': self.student.nationality_id,
                'domicile': self.student.domicile_id,
                'ethnicity': self.student.ethnicity_id,
                'religion_or_belief': self.student.religion_or_belief_id,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.student.refresh_from_db()
        self.assertEqual(self.student.surname, 'newsurname')


class TestLookup(LoggedInMixin, TestCase):
    url = reverse_lazy('student:lookup')

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.student = factories.StudentFactory(sits_id=123, husid=456)

    def test_lookup_by_sits_id(self):
        response = self.client.post(self.url, data={'sits_id': 123})
        self.assertRedirects(response, self.student.get_absolute_url())

    def test_lookup_by_husid(self):
        response = self.client.post(self.url, data={'husid': 456})
        self.assertRedirects(response, self.student.get_absolute_url())

    def test_failed_lookup(self):
        response = self.client.post(self.url, data={'husid': 789})
        self.assertRedirects(response, reverse('student:search'))


class TestDiet(LoggedInViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.DietFactory()
        cls.url = reverse('student:edit-diet', kwargs={'student_id': cls.student.student_id})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_edit_diet(self):
        self.assertIsNone(self.student.type)
        response = self.client.post(self.url, data={'type': models.Diet.Types.GLUTEN_FREE.value})

        self.student.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.student.type, models.Diet.Types.GLUTEN_FREE.value)


class TestEmergencyContact(LoggedInViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.emergency_contact = factories.EmergencyContactFactory()
        cls.url = reverse('student:emergency-contact:edit', kwargs={'student_id': cls.emergency_contact.student_id})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_edit_emergency_contact(self):
        response = self.client.post(self.url, data={'name': 'testname', 'email': 'test@test.com'})

        self.emergency_contact.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.emergency_contact.name, 'testname')
        self.assertEqual(self.emergency_contact.email, 'test@test.com')

    def test_delete_emergency_contact(self):
        self.client.post(reverse('student:emergency-contact:delete', kwargs={'pk': self.emergency_contact.pk}))
        with self.assertRaises(models.EmergencyContact.DoesNotExist):
            self.emergency_contact.refresh_from_db()


class TestMerge(LoggedInViewTestMixin, TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.student_a, cls.student_b = factories.StudentFactory.create_batch(size=2)
        querystring = urlencode({'student': [cls.student_a.pk, cls.student_b.pk]}, doseq=True)
        cls.url = reverse('student:merge') + '?' + querystring

    def test_merge(self):
        response = self.client.post(self.url, data={'records': [self.student_a.pk, self.student_b.pk]})
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(models.Student.DoesNotExist):
            self.student_a.refresh_from_db()
            self.student_b.refresh_from_db()

    def test_requires_two(self):
        response = self.client.post(self.url, data={'records': [self.student_a.pk]})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    @patch('apps.student.services.merge.merge_multiple_students')
    def test_merge_errors_displayed(self, patched_method):
        patched_method.side_effect = services.merge.CannotMergeError('test message')
        response = self.client.post(self.url, data={'records': [self.student_a.pk, self.student_b.pk]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test message')


class TestStudentMarketing(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = factories.StudentFactory()
        cls.url = reverse('student:marketing', kwargs={'pk': cls.student.pk})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_email_optin_success(self):
        self.assertFalse(self.student.email_optin)
        response = self.client.post(
            self.url,
            data={
                'email_optin': True,
                'email_optin_on': datetime(2020, 1, 1, 12),
                'email_optin_method': models.Student.MarketingOptinMethods.IN_PERSON,
            },
        )
        self.student.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.student.email_optin, True)
        self.assertEqual(self.student.email_optin_on, datetime(2020, 1, 1, 12))
        self.assertEqual(self.student.email_optin_method, models.Student.MarketingOptinMethods.IN_PERSON)
