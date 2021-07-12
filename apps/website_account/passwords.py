import hashlib

from django.contrib.auth import hashers, password_validation
from django.utils.crypto import get_random_string, pbkdf2


class LegacyPasswordHasher(hashers.PBKDF2PasswordHasher):
    """Legacy password hasher, allowing us to hash passwords to the same spec as our legacy website (web2py)"""

    algorithm = "pbkdf2"
    digest = hashlib.sha512
    iterations = 1000

    def encode(self, password, salt, iterations=None):
        # Override the standard encoding routine to encode the hash as hex rather than base64 and truncate at 40 chars
        # Alternately, this could run super().encode(), split the result by $, re-encode with hex, and reassemble
        assert password is not None
        assert salt and '$' not in salt
        iterations = iterations or self.iterations
        hash = pbkdf2(password, salt, iterations, digest=self.digest)
        hash = hash.hex()[:40]
        return "%s(%d,20,sha512)$%s$%s" % (self.algorithm, iterations, salt, hash)

    def salt(self) -> str:
        # w2p expects 16-char salt, so we use django's salt-generator with limited characters
        return get_random_string(length=16)


class PBKDF2SHA512PasswordHasherW2P(hashers.PBKDF2PasswordHasher):
    """
    Backwards-compatible passwords hasher.

    Should only be used for validation, not creation

    Will allow us to use legacy (web2py) website passwords on a new django site
    Will first require the conversion of old style (pbkdf2(<iters>,20,sha512)$<salt>$<hash>) records to a style
    compatible with Django (pbkdf2_w2p$<iters>$<salt>$<hash>)
    """

    algorithm = "pbkdf2_w2p"
    digest = hashlib.sha512
    iterations = 1000

    def encode(self, password, salt, iterations=None):
        # Override the standard encoding routine to encode the hash as hex rather than base64 and truncate at 40 chars
        # Alternately, this could run super().encode(), split the result by $, re-encode with hex, and reassemble
        assert password is not None
        assert salt and '$' not in salt
        iterations = iterations or self.iterations
        hash = pbkdf2(password, salt, iterations, digest=self.digest)
        hash = hash.hex()[:40]
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)


def validate_password(password: str) -> None:
    """
    Checks a password against our existing website password rules.
    Doesn't handle ValidationErrors, as they're handled by Forms, etc.
    """
    WEBSITE_PASSWORD_VALIDATORS = [
        password_validation.MinimumLengthValidator(12),
        password_validation.CommonPasswordValidator(),
        password_validation.NumericPasswordValidator(),
    ]
    password_validation.validate_password(password, password_validators=WEBSITE_PASSWORD_VALIDATORS)


def make_legacy_password(password: str, salt: str = None) -> str:
    return hashers.make_password(password, salt, hasher=LegacyPasswordHasher())
