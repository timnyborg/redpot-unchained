from parameterized import parameterized

from django.test import SimpleTestCase, TestCase

from .. import models, services


class TestGenerateHUSID(SimpleTestCase):
    @parameterized.expand(
        [
            (1999, 12, 9911560000120),
            (2018, 9833, 1811560098335),
            (2020, 9300, 2011560093001),
        ]
    )
    def test_generation(self, year, seed, result):
        self.assertEqual(services._generate_husid(academic_year=year, seed=seed), result)


class TestGettingNextHUSID(TestCase):
    def test_model_creation_and_increment(self):
        """Check that a non-existant NextHUSID model will be generated when first required, with a 'next' of 0"""
        with self.assertRaises(models.NextHUSID.DoesNotExist):
            models.NextHUSID.objects.get(year=2021)
        services.next_husid(2021)
        self.assertEqual(models.NextHUSID.objects.get(year=2021).next, 1)
        services.next_husid(2021)
        self.assertEqual(models.NextHUSID.objects.get(year=2021).next, 2)

    def test_validation(self):
        self.assertRaises(ValueError, services.next_husid, 0)
        self.assertRaises(ValueError, services.next_husid, 9999)
