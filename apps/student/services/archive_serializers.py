"""
The ModelSerializers necessary to archive a student record before a destructive merge
"""

from rest_framework.serializers import ModelSerializer

from apps.enrolment.models import Enrolment
from apps.qualification_aim.models import QualificationAim
from apps.student import models
from apps.website_account.models import WebsiteAccount


class EnrolmentSerializer(ModelSerializer):
    class Meta:
        model = Enrolment
        fields = '__all__'


class QualificationAimSerializer(ModelSerializer):
    enrolments = EnrolmentSerializer(many=True, read_only=True)

    class Meta:
        model = QualificationAim
        fields = '__all__'


class AddressSerializer(ModelSerializer):
    class Meta:
        model = models.Address
        fields = '__all__'


class EmailSerializer(ModelSerializer):
    class Meta:
        model = models.Email
        fields = '__all__'


class PhoneSerializer(ModelSerializer):
    class Meta:
        model = models.Phone
        fields = '__all__'


class OtherIDSerializer(ModelSerializer):
    class Meta:
        model = models.OtherID
        fields = '__all__'


class WebsiteAccountSerializer(ModelSerializer):
    class Meta:
        model = WebsiteAccount
        fields = '__all__'


class StudentSerializer(ModelSerializer):
    qualification_aims = QualificationAimSerializer(many=True, read_only=True)

    addresses = AddressSerializer(many=True, read_only=True)
    emails = EmailSerializer(many=True, read_only=True)
    phones = PhoneSerializer(many=True, read_only=True)
    website_accounts = WebsiteAccountSerializer(many=True, read_only=True)
    other_ids = OtherIDSerializer(many=True, read_only=True)

    class Meta:
        model = models.Student
        fields = '__all__'
