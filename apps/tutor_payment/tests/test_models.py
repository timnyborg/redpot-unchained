from django.test import SimpleTestCase

from . import factories


class TestPaymentApprovalCheck(SimpleTestCase):
    def setUp(self) -> None:
        self.object = factories.TutorFeeFactory.build()

    def test_success(self):
        self.assertTrue(self.object.approvable())

    def test_missing_appointment_id(self):
        self.object.tutor_module.tutor.appointment_id = None
        self.assertFalse(self.object.approvable())
        self.assertTrue(self.object.approval_errors())

    def test_missing_finance_code(self):
        self.object.tutor_module.module.activity_code = None
        self.assertFalse(self.object.approvable())
        self.assertTrue(self.object.approval_errors())

    def test_missing_employee_no(self):
        self.object.tutor_module.tutor.employee_no = None
        self.assertFalse(self.object.approvable())
        self.assertTrue(self.object.approval_errors())

    # todo: RTW test once implemented
