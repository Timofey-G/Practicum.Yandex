from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from recipes.models import Recipe


class User(AbstractUser):
    email = models.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name="Адрес электронной почты",
    )
    username = models.CharField(
        max_length=settings.MAX_LENGTH_USERNAME,
        unique=True,
        verbose_name="Логин",
    )
    first_name = models.CharField(
        max_length=settings.MAX_LENGTH_FIRST_NAME, verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=settings.MAX_LENGTH_LAST_NAME, verbose_name="Фамилия"
    )
    password = models.CharField(
        max_length=settings.MAX_LENGTH_PASSWORD, verbose_name="Пароль"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("id",)

    def __str__(self):
        return self.username[: settings.MAX_LENGTH_STR]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Подписка на",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("-author__id",)

        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_follow",
            )
        ]

    def __str__(self):
        return (
            f"Подписчик: {self.user.username[: settings.MAX_LENGTH_STR]}. "
            f"Подписка на: {self.author.username[: settings.MAX_LENGTH_STR]}"
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь, который добавил рецепт в избранное",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт в избранном",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ("-recipe__id",)
        unique_together = ("user", "recipe")

    def __str__(self):
        return (
            f"Пользователь: {self.user.username[: settings.MAX_LENGTH_STR]}. "
            f"Избранное: {self.recipe.name[: settings.MAX_LENGTH_STR]}"
        )


class ShoppingCart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipes = models.ManyToManyField(
        Recipe, related_name="shopping_carts", verbose_name="Рецепты"
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return (
            "Список покупок пользователя "
            f"{self.user.username[: settings.MAX_LENGTH_STR]}"
        )


@receiver(post_save, sender=User)
def create_user_shopping_cart(sender, instance, created, **kwargs):
    if created:
        ShoppingCart.objects.create(user=instance)
