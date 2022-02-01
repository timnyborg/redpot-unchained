from unittest import mock

from django import test
from django.contrib.auth.models import Permission
from django.urls import reverse_lazy

from apps.core.utils.tests import LoggedInViewTestMixin
from apps.student.tests.factories import EmailFactory
from apps.tutor.tests.factories import TutorModuleFactory

from .. import models


class TestNewView(LoggedInViewTestMixin, test.TestCase):
    url = reverse_lazy('proposal:new')
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Make the user appear as a DoS option
        permission = Permission.objects.get(codename='approve_proposal')
        cls.user.user_permissions.add(permission)

        cls.tutor_module = TutorModuleFactory()
        EmailFactory(student=cls.tutor_module.tutor.student)

    @mock.patch('apps.proposal.services.populate_from_module')
    def test_create(self, mocked_service: mock.MagicMock):
        response = self.client.post(self.url, data={'dos': self.user.username, 'tutor_module': self.tutor_module.pk})

        self.assertEqual(response.status_code, 302)
        proposal = models.Proposal.objects.last()
        self.assertEqual(proposal.dos, self.user)

        mocked_service.assert_called_with(proposal=proposal)


class TestEditView(LoggedInViewTestMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Make the user appear as a DoS option
        permission = Permission.objects.get(codename='approve_proposal')
        cls.user.user_permissions.add(permission)
        cls.tutor_module = TutorModuleFactory()
        cls.proposal = models.Proposal.objects.create(tutor=cls.tutor_module.tutor, module=cls.tutor_module.module)

        cls.url = cls.proposal.get_edit_url()

    def test_post(self):
        response = self.client.post(
            self.url, data={'title': 'something', 'dos': self.user.username, 'room_setup': models.RoomSetups.SEMINR}
        )

        self.assertEqual(response.status_code, 302)
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.dos, self.user)
