from datetime import datetime

import factory

from apps.core.tests.factories import UserFactory
from apps.enrolment.tests.factories import EnrolmentFactory

from .. import models


class AmendmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Amendment

    type_id = models.AmendmentTypes.AMENDMENT
    reason_id = 1
    enrolment = factory.SubFactory(EnrolmentFactory)
    requested_on = factory.LazyFunction(datetime.now)
    requested_by = factory.SubFactory(UserFactory)
    amount = factory.Faker('pydecimal', min_value=1, left_digits=4, right_digits=2)
