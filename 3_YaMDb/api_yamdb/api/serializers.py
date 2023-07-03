from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import username_validator, year_validator


class UsernameValidatorMixin:

    def validate_username(self, value):
        return username_validator(value)


class UserSerializer(UsernameValidatorMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class UsernameSerializer(UsernameValidatorMixin, serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.MAX_LENGTH_USERNAME,
        required=True
    )


class SignUpSerializer(UsernameSerializer):
    email = serializers.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        required=True,
    )


class TokenSerializer(UsernameSerializer):
    confirmation_code = serializers.CharField(
        max_length=settings.CODE_LENGTH,
        required=True,
    )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field="slug",
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug",
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )
        model = Title

    def validate_year(self, value):
        return year_validator(value)


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )
        read_only_fields = fields
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    score = serializers.IntegerField(
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

    def validate(self, data):
        request = self.context.get("request")
        if request.method != "POST":
            return data
        title_id = self.context.get("view").kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        if title.reviews.filter(author=request.user):
            raise serializers.ValidationError(
                "Вы не можете добавлять "
                "больше одного отзыва для произведения"
            )
        return data

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
