import factory

from .. import models


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Student

    firstname = factory.Faker('first_name')
    surname = factory.Faker('last_name')


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Address

    student = factory.SubFactory(StudentFactory)
    line1 = factory.Faker('street_address')
    postcode = factory.Faker('postcode')
    town = factory.Faker('city')
    is_default = True


class StudentWithAddressFactory(StudentFactory):
    address = factory.RelatedFactory(AddressFactory, factory_related_name='student')


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Email

    student = factory.SubFactory(StudentFactory)
    email = factory.Faker('email')


class MoodleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MoodleID

    student = factory.SubFactory(StudentFactory)
    moodle_id = factory.Sequence(lambda pk: 100000 + pk)


class PhoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Phone

    student = factory.SubFactory(StudentFactory)
    number = factory.Faker('numerify', text='########')
    type = models.Phone.PhoneTypeChoices.ALT_PHONE
    is_default = True


class OtherIDFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OtherID

    student = factory.SubFactory(StudentFactory)
    number = factory.Faker('numerify', text='########')
    type = models.OtherID.OtherIdTypeChoices.VISA_ID
