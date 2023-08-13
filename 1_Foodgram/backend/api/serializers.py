import base64
import binascii
import time

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow

User = get_user_model()


class UserFollowBaseSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return user.following.filter(
                author=getattr(obj, "author", obj)
            ).exists()
        return False


class RecipeBaseSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.shopping_carts.filter(user=user).exists()
        return False


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get("current_password") == attrs.get("new_password"):
            raise serializers.ValidationError(
                {"detail": "Новый пароль должен отличаться от текущего."}
            )
        return attrs

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not authenticate(username=user.username, password=value):
            raise ValidationError("Неправильный пароль.")


class UserReadSerializer(UserFollowBaseSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        read_only_fields = fields


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        read_only_fields = fields[1:]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeShortSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def get_image(self, obj):
        request = self.context["request"]
        return request.build_absolute_uri(obj.image.url)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.IntegerField(
        max_value=settings.MAX_INGREDIENT_AMOUNT,
        min_value=settings.MIN_INGREDIENT_AMOUNT,
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(RecipeBaseSerializer):
    author = UserReadSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        source="recipe_ingredients", many=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = fields


class RecipeCreateUpdateSerializer(RecipeBaseSerializer):
    author = UserReadSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source="recipe_ingredients", many=True
    )
    image = serializers.CharField()
    cooking_time = serializers.IntegerField(
        max_value=settings.MAX_COOKING_TIME,
        min_value=settings.MIN_COOKING_TIME,
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("is_favorited", "is_in_shopping_cart")

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipe_ingredients")
        tags_data = validated_data.pop("tags")

        image = validated_data.pop("image")
        data = self._decode_image(image)

        recipe = Recipe.objects.create(
            author=self.context["request"].user, image=data, **validated_data
        )
        self._create_recipe_ingredients(recipe, ingredients_data)
        recipe.tags.set(tags_data)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        image = validated_data.pop("image", None)
        if image:
            data = self._decode_image(image)
            instance.image = data

        ingredients_data = validated_data.pop("recipe_ingredients", None)
        if ingredients_data:
            instance.recipe_ingredients.all().delete()
            self._create_recipe_ingredients(instance, ingredients_data)

        tags_data = validated_data.pop("tags", None)
        if tags_data:
            instance.tags.set(tags_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def _decode_image(self, image):
        try:
            format, imgstr = image.split(";base64,")
            data = ContentFile(
                base64.b64decode(imgstr), name=f"{time.time()}.jpg"
            )
        except (binascii.Error, ValueError):
            raise ValidationError(
                f"Некорректное значение поля 'image': '{image}'. Ожидается "
                "формат base64: 'data:image/png;base64,<байт-код "
                "изображения>'."
            )
        return data

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(
                id=ingredient_data["ingredient"]["id"]
            )
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data["amount"],
            )
            recipe_ingredients.append(recipe_ingredient)
        RecipeIngredient.objects.bulk_create(recipe_ingredients)


class FollowSerializer(UserFollowBaseSerializer):
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()

    def get_recipes(self, obj):
        recipe_limits = self.context.get("recipes_limit")
        if recipe_limits:
            recipes = obj.author.recipes.all()[:recipe_limits]
        else:
            recipes = obj.author.recipes.all()

        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data

    def validate(self, attrs):
        user = self.context["request"].user
        author = self.context.get("author")
        if user == author:
            raise ValidationError("Вы не можете подписаться на самого себя.")

        return attrs
