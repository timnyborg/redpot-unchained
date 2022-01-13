import factory

from apps.module.tests.factories import ModuleFactory

from .. import models


class ProgrammeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Programme

    title = factory.Sequence(lambda n: f'Programme #{n}')

    # todo: replace with enums?
    division_id = 1
    portfolio_id = 1
    qualification_id = 1


class ProgrammeModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Programme

    programme = factory.SubFactory(ProgrammeFactory)
    module = factory.SubFactory(ModuleFactory)
