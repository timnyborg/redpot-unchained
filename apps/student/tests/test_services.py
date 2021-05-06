import pytest
from parameterized import parameterized

from .. import models, services


@parameterized.expand(
    [
        (1999, 12, 9911560000120),
        (2018, 9833, 1811560098335),
        (2020, 9300, 2011560093001),
    ]
)
def test_husid_generation(year, seed, result):
    assert services._generate_husid(academic_year=year, seed=seed) == result


@pytest.mark.django_db
def test_nexthusid_model_creation_and_increment():
    """Check that a non-existant NextHUSID model will be generated when first required, with a 'next' of 0"""
    with pytest.raises(models.NextHUSID.DoesNotExist):
        models.NextHUSID.objects.get(year=2021)
    services.next_husid(2021)
    assert models.NextHUSID.objects.get(year=2021).next == 1
    services.next_husid(2021)
    assert models.NextHUSID.objects.get(year=2021).next == 2


def test_nexthusid_validation():
    with pytest.raises(ValueError):
        services.next_husid(0)
    with pytest.raises(ValueError):
        services.next_husid(9999)
