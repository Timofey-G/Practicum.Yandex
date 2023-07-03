from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_name")

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(UsersURLTests.user)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            "/auth/signup/": "users/signup.html",
            "/auth/login/": "users/login.html",
            "/auth/password_change/": "users/password_change_form.html",
            "/auth/password_change/done/": "users/password_change_done.html",
            "/auth/password_reset/": "users/password_reset_form.html",
            "/auth/password_reset/done/": "users/password_reset_done.html",
            "/auth/reset/done/": "users/password_reset_complete.html",
            "/auth/reset/<uidb64>/<token>/": (
                "users/password_reset_confirm.html"),
            "/auth/logout/": "users/logged_out.html",
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = UsersURLTests.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location_for_anonymous(self):
        url_names = [
            "/auth/signup/",
            "/auth/login/",
            "/auth/password_reset/",
            "/auth/password_reset/done/",
            "/auth/reset/done/",
            "/auth/reset/<uidb64>/<token>/",
            "/auth/logout/",
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = UsersURLTests.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_for_authorized_user(self):
        url_names = [
            "/auth/password_change/",
            "/auth/password_change/done/",
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = UsersURLTests.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_on_auth_login(self):
        url_names = [
            "/auth/password_change/",
            "/auth/password_change/done/",
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = UsersURLTests.guest_client.get(address)
                self.assertRedirects(response, f"/auth/login/?next={address}")


class UsersViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_name")
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(UsersViewsTests.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse("users:signup"): "users/signup.html",
            reverse("users:login"): "users/login.html",
            reverse(
                "users:password_change_form",
            ): "users/password_change_form.html",
            reverse(
                "users:password_change_done",
            ): "users/password_change_done.html",
            reverse(
                "users:password_reset_form",
            ): "users/password_reset_form.html",
            reverse(
                "users:password_reset_done",
            ): "users/password_reset_done.html",
            reverse(
                "users:password_reset_complete"
            ): "users/password_reset_complete.html",
            reverse("users:logout"): "users/logged_out.html",
            reverse(
                "users:password_reset_confirm",
                args=["123", "123"],
            ): "users/password_reset_confirm.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = UsersViewsTests.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_page_show_correct_context(self):
        response = UsersViewsTests.guest_client.get(reverse("users:signup"))
        form_fields = {
            "first_name": forms.fields.CharField,
            "last_name": forms.fields.CharField,
            "username": forms.fields.CharField,
            "email": forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)


class UsersFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

    def test_users_signup(self):
        users_count = User.objects.count()
        form_data = {
            "username": "TestName",
            "password1": "Qwer4430",
            "password2": "Qwer4430",
        }
        UsersFormsTests.guest_client.post(
            reverse("users:signup"),
            data=form_data,
            follow=True,
        )
        self.assertEqual(User.objects.count(), users_count + 1)
