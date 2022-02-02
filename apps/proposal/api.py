from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Proposal
        fields = ['pk', 'title', 'tutor', 'module', 'status']


class ProposalViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    A collection of business-logic actions

    reset: return a proposal to the CREATED state, and nullify updated_fields
    """

    queryset = models.Proposal.objects.all()
    serializer_class = ProposalSerializer

    @action(detail=True, methods=['post'], url_name='reset')
    def reset(self, request, pk=None):
        proposal = self.get_object()
        proposal.status = models.Statuses.CREATED
        proposal.updated_fields = []
        proposal.save()
        return Response({'status': 'Proposal reset'})
