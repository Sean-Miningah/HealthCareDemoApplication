from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.core import mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class UserViewSetTests(APITestCase):
    def setUp(self):
        # Create a regular user
        self.user = User.objects.create_user(
            email='testuser@example.com', password='testpassword'
        )
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com', password='adminpassword', role='ADMIN'
        )
        # Get tokens for users
        self.user_token = Token.objects.create(user=self.user)
        self.admin_token = Token.objects.create(user=self.admin_user)

    def test_user_creation(self):
        url = reverse('user-list')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'password_confirmation': 'newpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_user_list_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_list_regular_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_self(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_user_detail_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_user_detail_other(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('user-detail', args=[self.admin_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_update_self(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('user-detail', args=[self.user.id])
        data = {'phone_number': '123-456-7890'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=self.user.id).phone_number, '123-456-7890')

    def test_user_update_other(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('user-detail', args=[self.admin_user.id])
        data = {'phone_number': '123-456-7890'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_login_success(self):
        url = reverse('token_obtain')
        data = {'email': 'testuser@example.com', 'password': 'testpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)

    def test_user_login_failure(self):
        url = reverse('token_obtain')
        data = {'email': 'testuser@example.com', 'password': 'wrongpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('user-logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_change_password(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('user-change-password')
        data = {'old_password': 'testpassword', 'new_password': 'newpassword', 'new_password_confirmation': 'newpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh the user instance from the database
        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password('newpassword'))

    def test_change_password_wrong_old_password(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('user-change-password')
        data = {'old_password': 'wrongpassword', 'new_password': 'newpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_reset_password_request(self):
    #     url = reverse('user-reset-password-request')
    #     data = {'email': 'testuser@example.com'}
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertIn('reset your password', mail.outbox[0].body)

    # def test_reset_password_confirm(self):
    #     # First, request a password reset
    #     url_request = reverse('user-reset-password-request')
    #     data_request = {'email': 'testuser@example.com'}
    #     self.client.post(url_request, data_request)

    #     # Extract uid and token from the email
    #     email_body = mail.outbox[0].body
    #     reset_link_start = email_body.find(f"{settings.FRONTEND_URL}/reset-password/")
    #     reset_link = email_body[reset_link_start:]
    #     uid, token = reset_link.split('/')[-2:]

    #     # Now, confirm the password reset
    #     url_confirm = reverse('user-reset-password-confirm')
    #     data_confirm = {'uid': uid, 'token': token, 'new_password': 'newpassword123'}
    #     response = self.client.post(url_confirm, data_confirm)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(self.user.check_password('newpassword123'))

    # def test_reset_password_confirm_invalid_token(self):
    #     url_confirm = reverse('user-reset-password-confirm')
    #     data_confirm = {'uid': 'invalid_uid', 'token': 'invalid_token', 'new_password': 'newpassword123'}
    #     response = self.client.post(url_confirm, data_confirm)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        url = reverse('user-update-profile')
        data = {'phone_number': '987-654-3210'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=self.user.id).phone_number, '987-654-3210')

class CustomObtainAuthTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com', password='testpassword'
        )

    def test_custom_obtain_auth_token(self):
        url = reverse('token_obtain')
        data = {'email': 'testuser@example.com', 'password': 'testpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
