from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')

    def test_create_user_sets_usable_password(self):
        user = User.objects.create_user(email='driver@example.com', password='testpass123')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_sets_flags(self):
        admin = User.objects.create_superuser(email='boss@example.com', password='testpass123')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class GroupMigrationTests(TestCase):
    def test_customers_drivers_admin_groups_exist(self):
        names = set(Group.objects.values_list('name', flat=True))
        self.assertTrue({'Customers', 'Drivers', 'Admin'}.issubset(names))


class RegisterViewTests(TestCase):
    def setUp(self):
        self.url = reverse('accounts:register')
        self.valid_data = {
            'email': 'customer@example.com',
            'email2': 'customer@example.com',
            'password1': 'a-strong-password-123',
            'password2': 'a-strong-password-123',
        }

    def test_valid_registration_creates_user_and_logs_in(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, reverse('core:home'))

        user = User.objects.get(email='customer@example.com')
        self.assertTrue(user.groups.filter(name='Customers').exists())

        response = self.client.get(reverse('core:home'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_mismatched_emails_rejected(self):
        data = {**self.valid_data, 'email2': 'someone-else@example.com'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='customer@example.com').exists())

    def test_mismatched_passwords_rejected(self):
        data = {**self.valid_data, 'password2': 'a-different-password-456'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='customer@example.com').exists())

    def test_duplicate_email_rejected(self):
        User.objects.create_user(email='customer@example.com', password='existing-password-123')
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='customer@example.com').count(), 1)


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='customer@example.com', password='testpass123')
        self.url = reverse('accounts:login')

    def test_valid_login_authenticates(self):
        response = self.client.post(self.url, {'username': 'customer@example.com', 'password': 'testpass123'})
        self.assertRedirects(response, reverse('core:home'))
        response = self.client.get(reverse('core:home'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_password_rejected(self):
        response = self.client.post(self.url, {'username': 'customer@example.com', 'password': 'wrong-password'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='customer@example.com', password='testpass123')
        self.client.login(username='customer@example.com', password='testpass123')
        self.url = reverse('accounts:logout')

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post_logs_out(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('core:home'))
        response = self.client.get(reverse('core:home'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class PasswordResetFlowTests(TestCase):
    """
    Regression test: Django's PasswordResetView/PasswordResetConfirmView
    default success_url reverses a bare 'password_reset_done' /
    'password_reset_complete' name, which doesn't exist once urls.py is
    namespaced under 'accounts:' - it must be overridden explicitly.
    """

    def setUp(self):
        self.user = User.objects.create_user(email='customer@example.com', password='testpass123')

    def test_request_reset_redirects_to_done_page(self):
        response = self.client.post(reverse('accounts:password_reset'), {'email': self.user.email})
        self.assertRedirects(response, reverse('accounts:password_reset_done'))

    def test_full_reset_flow_changes_password(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        # Following the emailed link performs a redirect to a session-based
        # URL (Django's PasswordResetConfirmView anti-token-leak behaviour).
        confirm_url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(confirm_url, follow=True)
        self.assertEqual(response.status_code, 200)

        session_url = response.redirect_chain[-1][0]
        response = self.client.post(session_url, {
            'new_password1': 'a-new-strong-password-456',
            'new_password2': 'a-new-strong-password-456',
        })
        self.assertRedirects(response, reverse('accounts:password_reset_complete'))

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('a-new-strong-password-456'))
