from datetime import datetime

from rest_framework import authentication, mixins, permissions, serializers, viewsets
from rest_framework.decorators import action

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect

from . import models, services


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Proposal
        fields = ['pk', 'title', 'tutor', 'module', 'status']


class ProposalViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    A collection of business-logic actions

    Standard lifecycle:
      send-to-tutor: emails the tutor with a link to the proposal,
      remind-tutor: emails a reminder to the tutor with a link to the proposal,
      remind-dos: emails a reminder to the DoS with a link to the proposal,
      mark-complete: sends completion emails and updates the module with the proposal data

    Additional admin tools:
      reset: return a proposal to the CREATED state, and nullify updated_fields,
      submit-as-tutor: fakes a tutor submission, updating the status and emailing the DoS,
      approve-as-dos: fakes a DoS approval, updating the status and emailing the admin,
      update-from-module: replace the proposal's content with data from the source module
    """

    queryset = models.Proposal.objects.all()
    serializer_class = ProposalSerializer
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [permissions.DjangoModelPermissions]

    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        proposal = self.get_object()
        proposal.status = models.Statuses.CREATED
        proposal.updated_fields = []
        proposal.save()
        messages.success(request, 'Proposal reset')
        return redirect(proposal.get_edit_url())

    @action(detail=True, methods=['post'])
    def send_to_tutor(self, request, pk=None):
        proposal = self.get_object()
        missing_fields = proposal.missing_fields()
        if proposal.limited and missing_fields:
            fields = ', '.join(missing_fields).replace('_', ' ')
            messages.error(request, f"Some fields must be filled by admin first ({fields})")
            return redirect(proposal.get_edit_url())

        proposal.status = models.Statuses.TUTOR
        proposal.updated_fields = []
        proposal.save()

        # todo: skip a step of the tutor is a dos?
        services.email_tutor_prompt(proposal=proposal)

        messages.success(request, 'Sent for tutor review')
        return redirect(proposal.get_edit_url())

    @action(detail=True, methods=['post'])
    def remind_tutor(self, request, pk=None):
        proposal = self.get_object()
        proposal.reminded_on = datetime.now()
        proposal.save()

        services.email_tutor_prompt(proposal=proposal, reminder=True)

        messages.success(request, 'Reminder sent')
        return redirect(proposal.get_edit_url())

    @action(detail=True, methods=['post'])
    def remind_dos(self, request, pk=None):
        proposal = self.get_object()

        services.email_dos_prompt(proposal=proposal, reminder=True)

        messages.success(request, 'Reminder sent')
        return redirect(proposal.get_edit_url())

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        proposal = self.get_object()
        proposal.status = models.Statuses.COMPLETE
        proposal.admin_approve = datetime.now()
        proposal.updated_fields = []
        proposal.save()

        services.update_module(proposal=proposal)
        services.email_tutor_on_completion(proposal=proposal)

        messages.success(request, 'Proposal complete – module details updated')
        return redirect(proposal.module)

    @action(detail=True, methods=['post'])
    def submit_as_tutor(self, request, pk=None):
        proposal = self.get_object()
        proposal.status = models.Statuses.DOS
        proposal.tutor_approve = datetime.now()
        proposal.save()

        services.email_dos_prompt(proposal=proposal)
        services.email_tutor_submission_confirmation(proposal=proposal)
        services.email_admin_submission_confirmation(proposal=proposal)

        messages.success(request, 'Sent for DoS approval')
        return redirect(proposal.get_edit_url())

    @action(detail=True, methods=['post'])
    def approve_as_dos(self, request, pk=None):
        proposal = self.get_object()
        proposal.status = models.Statuses.ADMIN
        proposal.dos_approve = datetime.now()
        proposal.save()

        services.email_admin_prompt(proposal=proposal)

        messages.success(request, 'Sent for administrator approval')
        return redirect(proposal.get_edit_url())

    @action(detail=True, methods=['post'])
    def update_from_module(self, request, pk=None):
        proposal = self.get_object()
        services.populate_from_module(proposal=proposal)
        messages.success(request, "Proposal updated with module's details")
        return redirect(proposal.get_edit_url())
