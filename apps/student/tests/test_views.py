from datetime import date

from freezegun import freeze_time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.testcases import SimpleTestCase
from django.urls import reverse

from apps.qualification_aim.tests import factories
from apps.tutor.models import Tutor
from apps.tutor.tests.factories import TutorFactory, TutorModuleFactory

from ..models import Student
from .factories import StudentFactory


class TestViewsWithoutLogin(TestCase):
    def test_views_require_login(self):
        response = self.client.get(reverse('student:search'))
        self.assertEqual(response.status_code, 302)


class TestSearch(TestCase):
    url = reverse('student:search')

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = StudentFactory(
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
        cls.student = StudentFactory()
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
        newest_student = Student.objects.last()
        self.assertEqual(newest_student.surname, 'smith')
        self.assertEqual(newest_student.emails.first().email, 'test@test.net')


class TestCreateEmail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = StudentFactory()
        cls.url = reverse('student:email-create', kwargs={'student_id': cls.student.pk})
        cls.invalid_url = reverse('student:email-create', kwargs={'student_id': 0})

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


class TestMakeTutor(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = StudentFactory()
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
        cls.student = StudentFactory()
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
        cls.student = StudentFactory()
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
        cls.student = StudentFactory()
        cls.url = reverse('student:view', args=[cls.student.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_student_is_tutor(self):
        response = self.client.get(self.url)
        self.assertIsNone(response.context['tutor'])


@freeze_time('2020-01-01')
class TestStudentRTWExpired(SimpleTestCase):
    def test_expired(self):
        tutor = TutorFactory.build(rtw_end_date=date(1999, 1, 1))
        self.assertTrue(tutor.rtw_expired())

    def test_not_expired(self):
        tutor = TutorFactory.build(rtw_end_date=date(2025, 1, 1))
        self.assertFalse(tutor.rtw_expired())


@freeze_time('2020-01-01')
class TestStudentRTWExpiresSoon(SimpleTestCase):
    def test_expiring_soon(self):
        tutor = TutorFactory.build(rtw_end_date=date(1999, 6, 1))
        self.assertTrue(tutor.rtw_expires_soon())

    def test_not_expiring_soon(self):
        tutor = TutorFactory.build(rtw_end_date=date(2025, 1, 1))
        self.assertFalse(tutor.rtw_expires_soon())


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
        cls.qa = factories.QualificationAimFactory()
        cls.url = reverse('student:view', args=[cls.qa.student.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_student_enrolment(self):
        response = self.client.get(self.url)
        self.assertIsNotNone(response.context['qa_list'])
        self.assertEquals(response.context['qa_list'][0].programme.qualification.id, 1)
        self.assertTrue(response.context['qa_list'][0].non_accredited)
