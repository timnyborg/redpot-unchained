from apps.core.models import User


class LoggedInMixin:
    user: User
    superuser: bool = False

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', is_superuser=cls.superuser, email='testuser@conted.ox.ac.uk'
        )

    def setUp(self):
        self.client.force_login(self.user)


class LoggedInViewTestMixin(LoggedInMixin):
    """Convience mixin for testing views that require login
    Creates a user, and forces a login before each test.
    Automatically tests getting the view url
    """

    url = ''

    def get_url(self):
        if not self.url:
            raise ValueError(f'You must set {self.__class__.__name__}.url')
        return self.url

    def test_get(self, *args, **kwargs):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
