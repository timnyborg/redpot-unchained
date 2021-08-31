from django import test
from django.contrib.auth.models import Permission
from django.core.management import call_command


class TestMigratePermissions(test.TestCase):
    @staticmethod
    def fetch_permission() -> Permission:
        return Permission.objects.get(content_type__app_label='amendment', codename='approve')

    @classmethod
    def setUpTestData(cls):
        # Remove a permission to test its recreation
        permission = cls.fetch_permission()
        permission.delete()

    def test_all_apps(self):
        """Check a permission is recreated when command called with no args"""
        call_command('migratepermissions')
        try:
            self.fetch_permission()
        except Permission.DoesNotExist:
            self.fail('Permission `amendment.approve` does not exist')

    def test_specified_apps(self):
        """Check a permission is recreated when command called with app args"""
        call_command('migratepermissions', ['student', 'amendment'])
        try:
            self.fetch_permission()
        except Permission.DoesNotExist:
            self.fail('Permission `amendment.approve` does not exist')

    def test_wrong_specified_apps(self):
        """Check a permission is not recreated when command called with other app args"""
        call_command('migratepermissions', ['student', 'enrolment'])
        with self.assertRaises(Permission.DoesNotExist):
            self.fetch_permission()
