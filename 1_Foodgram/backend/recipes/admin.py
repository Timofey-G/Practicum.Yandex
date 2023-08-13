from django.conf import settings
from django.contrib import admin
from django.utils.html import mark_safe

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "text",
        "display_ingredients",
        "cooking_time",
        "display_tag",
        "image",
        "display_author",
        "display_favorite_count",
    )
    list_display_links = ("id", "name")
    search_fields = ("name", "text", "cooking_time")
    inlines = (RecipeIngredientInline,)
    list_filter = ("name", "tags", "author")

    def display_author(self, obj):
        return obj.author.username

    def display_ingredients(self, obj):
        return mark_safe(
            "<br>".join(
                [
                    f"{ri.ingredient.name}, {ri.amount} "
                    f"{ri.ingredient.measurement_unit}"
                    for ri in obj.recipe_ingredients.all()
                ]
            )
        )

    def display_tag(self, obj):
        return mark_safe(
            "<br>".join([f"{tag.name}" for tag in obj.tags.all()])
        )

    def display_favorite_count(self, obj):
        return obj.favorites.count()

    display_author.short_description = "Автор"
    display_ingredients.short_description = "Ингредиенты"
    display_tag.short_description = "Теги"
    display_favorite_count.short_description = (
        "Количество добавлений в избранное"
    )


class RecipeDisplayBaseAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")

    def display_recipes(self, obj):
        return mark_safe(
            "<br>".join(
                [
                    recipe.name
                    for recipe in obj.recipes.all()[
                        : settings.RECENT_RECIPES_LIMIT
                    ]
                ]
            )
        )

    display_recipes.short_description = "Последние рецепты"


@admin.register(Tag)
class TagAdmin(RecipeDisplayBaseAdmin):
    list_display = RecipeDisplayBaseAdmin.list_display + (
        "color",
        "slug",
        "display_recipes",
    )


@admin.register(Ingredient)
class IngredientAdmin(RecipeDisplayBaseAdmin):
    list_display = RecipeDisplayBaseAdmin.list_display + (
        "measurement_unit",
        "display_recipes",
    )
    list_filter = ("name",)
