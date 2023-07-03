from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Имя", max_length=200)
    slug = models.SlugField("Адрес", unique=True)
    description = models.TextField("Описание")

    class Meta:
        verbose_name = "Сообщество"
        verbose_name_plural = "Сообщества"

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        "Текст",
        help_text="Введите текст поста",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Выберите группу, к которой будет относиться пост",
    )
    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        blank=True,
        help_text="Загрузите изображение",
    )
    likes = models.ManyToManyField(
        User,
        blank=True,
        related_name="likes",
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-created"]

    def __str__(self):
        return self.text[: settings.AMOUNT_OF_SYMBOLS]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    text = models.TextField("Текст комментария", max_length=200)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created"]

    def __str__(self):
        return self.text[: settings.AMOUNT_OF_SYMBOLS]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Подписка",
    )

    class Meta:
        verbose_name = "Подписчик/подписка"
        verbose_name_plural = "Подписчики/подписки"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_follow",
            )
        ]

    def __str__(self):
        return (f"Подписчик: {self.user.username}. "
                f"Подписка: {self.author.username}")
