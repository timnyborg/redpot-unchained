from unittest import mock

from rest_framework import status, test

from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin
from apps.proposal.tests import factories

from .. import models


@mock.patch('apps.proposal.api.services')
class TestAPIViewSet(LoggedInMixin, test.APITestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.proposal = factories.ProposalFactory(limited=True)

    def test_send_to_tutor_incomplete(self, patched_module: mock.MagicMock):
        """Will fail to update if columns missing data (limited-editing proposal)"""
        response = self.client.post(reverse('proposal:api:proposal-send-to-tutor', args=[self.proposal.pk]))

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, models.Statuses.CREATED)
        patched_module.email_tutor_prompt.assert_not_called()

    @mock.patch('apps.proposal.models.Proposal.missing_fields', return_value=[])
    def test_send_to_tutor(self, patched_method, patched_module: mock.MagicMock):
        response = self.client.post(reverse('proposal:api:proposal-send-to-tutor', args=[self.proposal.pk]))

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, models.Statuses.TUTOR)
        patched_module.email_tutor_prompt.assert_called()

    def test_remind_tutor(self, patched_module: mock.MagicMock):
        self.client.post(reverse('proposal:api:proposal-remind-tutor', args=[self.proposal.pk]))
        patched_module.email_tutor_prompt.assert_called_with(proposal=self.proposal, reminder=True)

    def test_remind_dos(self, patched_module: mock.MagicMock):
        self.client.post(reverse('proposal:api:proposal-remind-dos', args=[self.proposal.pk]))
        patched_module.email_dos_prompt.assert_called_with(proposal=self.proposal, reminder=True)

    def test_mark_complete(self, patched_module: mock.MagicMock):
        self.client.post(reverse('proposal:api:proposal-mark-complete', args=[self.proposal.pk]))

        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, models.Statuses.COMPLETE)
        patched_module.update_module.assert_called_with(proposal=self.proposal)
        patched_module.email_tutor_on_completion.assert_called_with(proposal=self.proposal)

    def test_reset(self, patched_module: mock.MagicMock):
        self.proposal.status = models.Statuses.COMPLETE
        self.proposal.save()

        self.client.post(reverse('proposal:api:proposal-reset', args=[self.proposal.pk]))

        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, models.Statuses.CREATED)

    def test_submit_as_tutor(self, patched_module: mock.MagicMock):
        self.client.post(reverse('proposal:api:proposal-submit-as-tutor', args=[self.proposal.pk]))

        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, models.Statuses.DOS)
        patched_module.email_dos_prompt.assert_called_with(proposal=self.proposal)

    def test_approve_as_dos(self, patched_module: mock.MagicMock):
        self.client.post(reverse('proposal:api:proposal-approve-as-dos', args=[self.proposal.pk]))

        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, models.Statuses.ADMIN)
        patched_module.email_admin_prompt.assert_called_with(proposal=self.proposal)

    def test_update_from_module(self, patched_module: mock.MagicMock):
        self.client.post(reverse('proposal:api:proposal-update-from-module', args=[self.proposal.pk]))
        patched_module.populate_from_module.assert_called_with(proposal=self.proposal)
