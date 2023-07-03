import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username="TestName")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание группы",
        )
        cls.post = Post.objects.create(
            text="Первый тестовый текст",
            group=cls.group,
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def compare_posts_by_fields(self, form_data, flag=False):
        if flag:
            post = Post.objects.get(id=PostCreateFormTests.post.id)
            self.assertEqual(post.group, None)
        else:
            post = Post.objects.latest("id")
            self.assertEqual(post.group.id, form_data["group"])
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(
            post.author.username,
            PostCreateFormTests.user.username,
        )

    def test_post_create(self):
        form_data = {
            "text": "Второй тестовый текст",
            "group": PostCreateFormTests.group.id,
        }
        PostCreateFormTests.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        PostCreateFormTests.compare_posts_by_fields(self, form_data)

    def test_post_edit(self):
        form_data = {"text": "Измененный первый тестовый текст"}
        PostCreateFormTests.authorized_client.post(
            reverse(
                "posts:post_edit",
                args={PostCreateFormTests.post.id},
            ),
            data=form_data,
            follow=True,
        )
        PostCreateFormTests.compare_posts_by_fields(self, form_data, True)

    def test_post_create_with_image(self):
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif",
        )
        form_data = {
            "text": "Третий тестовый текст",
            "image": uploaded,
        }
        PostCreateFormTests.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                image=f"posts/{uploaded.name}",
            ).exists()
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username="TestName")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post = Post.objects.create(
            text="Первый тестовый текст",
            author=cls.user,
        )

    def test_comment_create(self):
        form_data = {"text": "Тестовый комментарий"}
        CommentCreateFormTests.authorized_client.post(
            reverse(
                "posts:add_comment",
                args=[CommentCreateFormTests.post.id],
            ),
            data=form_data,
            follow=True,
        )
        response = self.client.get(
            reverse(
                "posts:post_detail",
                args=[CommentCreateFormTests.post.id],
            )
        )
        self.assertIn(
            Comment.objects.get(
                text=form_data["text"],
                post=CommentCreateFormTests.post.id,
            ),
            response.context["comments"],
        )
