from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        group = PostModelTest.group
        field_self = {
            post: post.text[: settings.AMOUNT_OF_SYMBOLS],
            group: group.title,
        }
        for field, expected_value in field_self.items():
            with self.subTest(field=field):
                self.assertEqual(str(field), expected_value)

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value,
                )

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            "text": "Введите текст поста",
            "group": "Выберите группу, к которой будет относиться пост",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value,
                )
