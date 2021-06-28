from django.contrib.auth import get_user_model


class LoggedInViewTestMixin:
    url = ''

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.extra_test_data()

    @classmethod
    def extra_test_data(cls):
        """Override this to create more test data after creating the user"""
        pass

    def setUp(self):
        self.client.force_login(self.user)
        self.extra_setup()

    def extra_setup(self):
        """Override this to do extra steps after logging in before each test"""
        pass

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
