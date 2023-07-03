from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import username_validator, year_validator


class User(AbstractUser):
    USER: str = "user"
    ADMIN: str = "admin"
    MODERATOR: str = "moderator"
    ROLE_CHOICES = [
        (USER, "Аутентифицированнный пользователь"),
        (MODERATOR, "Модератор"),
        (ADMIN, "Администратор"),
    ]

    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=settings.MAX_LENGTH_USERNAME,
        unique=True,
        validators=(username_validator,),
        error_messages={
            "unique": ("Пользователь с таким именем уже существует"),
        },
    )
    email = models.EmailField(
        verbose_name="Email",
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=settings.MAX_LENGTH_FIRST_NAME,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=settings.MAX_LENGTH_LAST_NAME,
        blank=True,
    )
    bio = models.TextField(verbose_name="Биография", blank=True)
    role = models.CharField(
        verbose_name="Роль",
        choices=ROLE_CHOICES,
        default=USER,
        max_length=max(len(role) for role, _ in ROLE_CHOICES)
    )
    confirmation_code = models.CharField(
        verbose_name="Код подтверждения",
        blank=True,
        null=True,
        max_length=settings.CODE_LENGTH,
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.get_username()


class NameSlugModel(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=settings.MAX_LENGTH_NAME
    )
    slug = models.SlugField(
        verbose_name="Идентификатор",
        max_length=settings.MAX_LENGTH_SLUG,
        unique=True
    )

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self):
        return self.name[:settings.AMOUNT_OF_SYMBOLS]


class Genre(NameSlugModel):
    class Meta(NameSlugModel.Meta):
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Category(NameSlugModel):
    class Meta(NameSlugModel.Meta):
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Title(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=settings.MAX_LENGTH_NAME
    )
    year = models.IntegerField(
        verbose_name="Год выпуска",
        validators=[year_validator]
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name="titles",
        verbose_name="Жанр",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="titles",
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ("name",)

    def __str__(self):
        return self.name[:settings.AMOUNT_OF_SYMBOLS]


class TextAuthorDateModel(models.Model):
    text = models.TextField(verbose_name="Текст",)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="Автор",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )

    def __str__(self):
        return str(
            f"Текст: {self.text[:settings.AMOUNT_OF_SYMBOLS]}, "
            f"Автор: {self.author.username[:settings.AMOUNT_OF_SYMBOLS]}"
        )

    class Meta:
        abstract = True
        ordering = ("-pub_date",)


class Review(TextAuthorDateModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Оценка отзыва",
        default=settings.MIN_VALUE_SCORE,
        validators=[
            MaxValueValidator(
                limit_value=settings.MAX_VALUE_SCORE,
                message=(
                    f"Ваша оценка не должна быть"
                    f"больше {settings.MAX_VALUE_SCORE}"
                ),
            ),
            MinValueValidator(
                limit_value=settings.MIN_VALUE_SCORE,
                message=(
                    f"Ваша оценка не должна быть"
                    f"меньше {settings.MIN_VALUE_SCORE}"
                ),
            ),
        ],
    )

    class Meta(TextAuthorDateModel.Meta):
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = (
            models.UniqueConstraint(
                fields=["title", "author"],
                name="reviews_author_title_one",
            ),
        )


class Comment(TextAuthorDateModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор отзыва",
    )

    class Meta(TextAuthorDateModel.Meta):
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
