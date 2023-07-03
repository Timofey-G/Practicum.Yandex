from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_creator = User.objects.create(username="creator")
        cls.user_outside = User.objects.create(username="outside")

        cls.authorized_client_creator = Client()
        cls.authorized_client_creator.force_login(cls.user_creator)
        cls.authorized_client_outside = Client()
        cls.authorized_client_outside.force_login(cls.user_outside)

        cls.group = Group.objects.create(
            title="Тестовое название",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user_creator,
            group=cls.group,
        )

    def tearDown(self):
        cache.clear()

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            "/": "posts/index.html",
            f"/group/{PostsURLTests.group.slug}/": "posts/group_list.html",
            f"/profile/{PostsURLTests.user_creator.username}/": (
                "posts/profile.html"),
            f"/posts/{PostsURLTests.post.id}/": "posts/post_detail.html",
            f"/posts/{PostsURLTests.post.id}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = PostsURLTests.authorized_client_creator.get(
                    address,
                )
                self.assertTemplateUsed(response, template)

    def test_url_unexisting_page(self):
        response = self.client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_exists_at_desired_location_for_anonymous(self):
        url_names = [
            "/",
            f"/group/{PostsURLTests.group.slug}/",
            f"/profile/{PostsURLTests.user_creator.username}/",
            f"/posts/{PostsURLTests.post.id}/",
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = PostsURLTests.authorized_client_creator.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_for_outside_user(self):
        response = PostsURLTests.authorized_client_creator.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_for_authorized_user(self):
        response = PostsURLTests.authorized_client_creator.get(
            f"/posts/{PostsURLTests.post.id}/edit/",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_anonymous_on_auth_login(self):
        response = self.client.get("/create/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/create/")

    def test_url_redirect_outside_user_on_post_detail(self):
        response = PostsURLTests.authorized_client_outside.get(
            f"/posts/{PostsURLTests.post.id}/edit/",
            follow=True,
        )
        self.assertRedirects(response, f"/posts/{PostsURLTests.post.id}/")

    def test_error_page(self):
        response = self.client.get("/nonexist-page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
