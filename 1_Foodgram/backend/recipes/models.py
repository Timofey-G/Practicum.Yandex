from django.conf import settings
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME, verbose_name="Название"
    )
    image = models.ImageField(upload_to="images/", verbose_name="Картинка")
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        "Ingredient",
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        "Tag", related_name="recipes", verbose_name="Теги"
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(settings.MIN_COOKING_TIME),
            MaxValueValidator(settings.MAX_COOKING_TIME),
        ],
        verbose_name="Время приготовления (в минутах)",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-id",)

    def __str__(self):
        return self.name[: settings.MAX_LENGTH_STR]


class Tag(models.Model):
    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        unique=True,
        verbose_name="Название",
    )
    color = models.CharField(
        max_length=settings.MAX_LENGTH_COLOR,
        unique=True,
        verbose_name="Цветовой HEX-код",
        validators=[
            RegexValidator(
                regex="^#[0-9A-Fa-f]{6}$",
                message="Цвет должен быть в формате HEX, например #AF09fa",
                code="invalid_color",
            ),
        ],
    )
    slug = models.SlugField(
        max_length=settings.MAX_LENGTH_SLUG,
        unique=True,
        verbose_name="Идентификатор",
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("id",)

    def __str__(self):
        return self.name[: settings.MAX_LENGTH_STR]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME, verbose_name="Название"
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LENGTH_UNIT, verbose_name="Единицы измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)
        unique_together = ("name", "measurement_unit")
        indexes = [
            models.Index(fields=["name"], name="ingredient_name_idx"),
        ]

    def __str__(self):
        return self.name[: settings.MAX_LENGTH_STR]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепты",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipes",
        verbose_name="Ингредиенты",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(settings.MIN_INGREDIENT_AMOUNT),
            MaxValueValidator(settings.MAX_INGREDIENT_AMOUNT),
        ],
    )

    class Meta:
        ordering = ("-recipe__id",)
