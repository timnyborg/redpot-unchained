from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from .. import passwords


class TestPasswordHashers(SimpleTestCase):
    def test_legacy_hashing(self):
        password = 'qwer1234qwer'
        salt = 'ba4c40c1f2475bec'
        expected = 'pbkdf2(1000,20,sha512)$ba4c40c1f2475bec$c2755a86c3c50899789947e7404959eff7bdf3c9'
        self.assertEqual(
            passwords.make_legacy_password(password, salt),
            expected,
        )

    def test_legacy_salt(self):
        """Check that the legacy hasher returns 16 digit salt"""
        self.assertEqual(len(passwords.LegacyPasswordHasher().salt()), 16)

    def test_backwards_compatible_hashing(self):
        password = 'qwer1234qwer'
        salt = 'ba4c40c1f2475bec'
        expected = 'pbkdf2_w2p$1000$ba4c40c1f2475bec$c2755a86c3c50899789947e7404959eff7bdf3c9'
        self.assertEqual(passwords.PBKDF2SHA512PasswordHasherW2P().encode(password, salt), expected)

    def test_minimum_password_requirement(self):
        password = '1234'
        with self.assertRaises(ValidationError):
            passwords.validate_password(password)

    def test_valid_password(self):
        password = '1234qwer1234'
        try:
            passwords.validate_password(password)
        except ValidationError as e:
            self.fail(f'Password failed validation: {e}')
