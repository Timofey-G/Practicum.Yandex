from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        url_names = [
            "/about/author/",
            "/about/tech/",
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = StaticPagesURLTests.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        templates_url_names = {
            "/about/author/": "about/author.html",
            "/about/tech/": "about/tech.html",
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = StaticPagesURLTests.guest_client.get(address)
                self.assertTemplateUsed(response, template)


class StaticPagesViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse("about:author"): "about/author.html",
            reverse("about:tech"): "about/tech.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = StaticPagesViewTests.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
