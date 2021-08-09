from django import test

from apps.tutor.models import RightToWorkType

from . import factories


class TestPaymentApprovalCheck(test.SimpleTestCase):
    def setUp(self) -> None:
        self.object = factories.TutorFeeFactory.build(
            tutor_module__tutor__rtw_type=RightToWorkType.PERMANENT,
        )

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

    def test_missing_right_to_work(self):
        self.object.tutor_module.tutor.rtw_type = None
        self.assertFalse(self.object.approvable())
        self.assertTrue(self.object.approval_errors())
