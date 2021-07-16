from django import test

from apps.fee.tests.factories import FeeFactory
from apps.module.tests.factories import ModuleFactory

from .. import datatables


class TestAddFeesDatatable(test.TestCase):
    """Test that the datatable renders the correct places remaining for different fee types"""

    @classmethod
    def setUpTestData(cls):
        cls.module = ModuleFactory(
            single_places=10,
            twin_places=20,
        )
        cls.table = datatables.AddFeesTable(data={})

    def test_render_places_single(self):
        fee = FeeFactory.build(is_single_accom=True, module=self.module)
        self.assertEqual(self.table.render_places_left(fee), self.module.single_places)

    def test_render_places_twin(self):
        fee = FeeFactory.build(is_twin_accom=True, module=self.module)
        self.assertEqual(self.table.render_places_left(fee), self.module.twin_places)

    def test_render_places_catering(self):
        fee = FeeFactory(is_catering=True, allocation=20)
        self.assertEqual(self.table.render_places_left(fee), fee.allocation)
        fee.allocation = None
        fee.save()
        self.assertEqual(self.table.render_places_left(fee), '∞')

    def test_render_places_other(self):
        fee = FeeFactory.build()
        self.assertEqual(self.table.render_places_left(fee), '—')
