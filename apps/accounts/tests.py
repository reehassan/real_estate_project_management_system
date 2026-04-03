from django.test import TestCase
from apps.accounts.models import User

class UserAuthTest(TestCase):

    def setUp(self):
        # Create users with different roles
        self.owner = User.objects.create_user(
            username='owner',
            password='test123',
            Role='OWNER'
        )

        self.staff = User.objects.create_user(
            username='staff',
            password='test123',
            Role='STAFF'
        )

        self.customer = User.objects.create_user(
            username='customer',
            password='test999',
            Role='CUSTOMER'
        )

    def test_owner_can_login(self):
        login = self.client.login(username='owner', password='test123')
        self.assertTrue(login)

    def test_staff_can_login(self):
        login = self.client.login(username='staff', password='test123')
        self.assertTrue(login)

    def test_customer_can_login(self):
        login = self.client.login(username='customer', password='test999')
        self.assertTrue(login)