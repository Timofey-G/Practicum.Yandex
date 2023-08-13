import io

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Case, F, Q, Sum, When
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Favorite, Follow, ShoppingCart

from .permissions import IsAuthorOrIsAuthenticatedOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          PasswordChangeSerializer,
                          RecipeCreateUpdateSerializer, RecipeReadSerializer,
                          RecipeShortSerializer, TagSerializer,
                          UserCreateSerializer, UserReadSerializer)

User = get_user_model()


class PageNumberLimitPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "limit"
    max_page_size = 1000


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "delete")
    queryset = User.objects.all()
    pagination_class = PageNumberLimitPagination

    def destroy(self, request, pk=None):
        return Response(
            {"detail": 'Метод "DELETE" не разрешен.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def get_permissions(self):
        if self.action in ("retrieve", "list", "create"):
            permission_classes = (AllowAny,)
        else:
            permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "set_password":
            return PasswordChangeSerializer
        if self.action in ("subscriptions", "subscribe"):
            return FollowSerializer
        return UserReadSerializer

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def set_password(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data.get("new_password"))
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def subscriptions(self, request):
        subscriptions = request.user.following.all()
        recipes_limit = self._get_recipes_limit(request)

        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(
            page if page is not None else subscriptions,
            many=True,
            context={"request": request, "recipes_limit": recipes_limit},
        )
        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )

    @action(detail=True, methods=["post", "delete"])
    def subscribe(self, request, pk=None):
        author = self.get_object()
        user = request.user
        serializer = self.get_serializer(data=request.data, context={
            "request": request,
            "author": author,
        })
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        recipes_limit = self._get_recipes_limit(request)

        if request.method == "POST":
            return self._handle_subscribe(user, author, request, recipes_limit)
        if request.method == "DELETE":
            return self._handle_unsubscribe(user, author)

    def _get_recipes_limit(self, request):
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                raise ValidationError(
                    {
                        "errors": (
                            "Некорректное значение 'recipes_limit': "
                            f"'{recipes_limit}'."
                        )
                    }
                )
        return recipes_limit

    def _handle_subscribe(self, user, author, request, recipes_limit):
        follower, created = Follow.objects.get_or_create(
            user=user, author=author
        )
        if not created:
            raise ValidationError(
                {"detail": "Вы уже подписаны на этого пользователя."}
            )
        serializer = self.get_serializer(
            follower,
            context={"request": request, "recipes_limit": recipes_limit},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _handle_unsubscribe(self, user, author):
        follower = Follow.objects.filter(user=user, author=author)
        if not follower.exists():
            raise ValidationError(
                {"detail": "Вы не подписаны на этого пользователя."}
            )
        follower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "patch", "delete")
    queryset = (
        Recipe.objects.select_related("author")
        .prefetch_related("recipe_ingredients__ingredient", "tags")
        .all()
    )
    permission_classes = (IsAuthorOrIsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {}

        if self.request.user.is_authenticated:
            queryset = self._filter_by_preference(
                queryset, "favorites", "is_favorited"
            )
            queryset = self._filter_by_preference(
                queryset, "shopping_carts", "is_in_shopping_cart"
            )

        author_id = self.request.query_params.get("author")
        if author_id:
            filters["author_id"] = author_id

        tags = self.request.query_params.getlist("tags")
        if tags:
            filters["tags__slug__in"] = tags

        return queryset.filter(**filters).distinct()

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return RecipeCreateUpdateSerializer
        if self.action in ("favorite", "shopping_cart"):
            return RecipeShortSerializer
        return RecipeReadSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == "POST":
            self._add_to_favorite(user, recipe)
            serializer = self.get_serializer(
                recipe, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            self._remove_from_favorite(user, recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == "POST":
            self._add_to_shopping_cart(user, recipe)
            serializer = self.get_serializer(
                recipe, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            self._remove_from_shopping_cart(user, recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_cart = get_object_or_404(ShoppingCart, user=request.user)
        ingredients = self._get_shopping_cart_ingredients(shopping_cart)
        content = self._generate_ingredients_content(ingredients)

        buffer = io.BytesIO()
        pdf_canvas, textobject = self._create_canvas_and_textobject(
            buffer, settings.PAGE_SIZE
        )

        textobject = self._draw_text_line(
            textobject,
            settings.FONT_NAME,
            settings.TITLE_FONT_SIZE,
            settings.TITLE_TEXT,
            settings.TITLE_X_POSITION,
            settings.TITLE_Y_POSITION,
        )
        textobject = self._draw_content(
            textobject,
            settings.FONT_NAME,
            settings.CONTENT_FONT_SIZE,
            content,
            settings.CONTENT_X_POSITION,
            settings.CONTENT_Y_POSITION,
        )
        textobject = self._draw_text_line(
            textobject,
            settings.FONT_NAME,
            settings.FOOTER_FONT_SIZE,
            settings.FOOTER_FIRST_TEXT,
            settings.FOOTER_FIRST_X_POSITION,
            settings.FOOTER_FIRST_Y_POSITION,
        )
        textobject = self._draw_text_line(
            textobject,
            settings.FONT_NAME,
            settings.FOOTER_FONT_SIZE,
            settings.FOOTER_SECOND_TEXT,
            settings.FOOTER_SECOND_X_POSITION,
            settings.FOOTER_SECOND_Y_POSITION,
        )

        self._draw_underline(
            pdf_canvas,
            settings.UNDERLINE_WIDTH,
            settings.FIRST_UNDERLINE_X1_POSITION,
            settings.FIRST_UNDERLINE_Y2_POSITION,
            settings.FIRST_UNDERLINE_X2_POSITION,
            settings.FIRST_UNDERLINE_Y2_POSITION,
        )
        self._draw_underline(
            pdf_canvas,
            settings.UNDERLINE_WIDTH,
            settings.SECOND_UNDERLINE_X1_POSITION,
            settings.SECOND_UNDERLINE_Y2_POSITION,
            settings.SECOND_UNDERLINE_X2_POSITION,
            settings.SECOND_UNDERLINE_Y2_POSITION,
        )

        self._finalize_document(pdf_canvas, textobject, buffer)

        filename = "shopping-list.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)

    def _filter_by_preference(self, queryset, field, param):
        param_value = self.request.query_params.get(param)
        if param_value == "1":
            queryset = queryset.filter(**{f"{field}__user": self.request.user})
        elif param_value == "0":
            queryset = queryset.exclude(
                **{f"{field}__user": self.request.user}
            )
        return queryset

    def _add_to_favorite(self, user, recipe):
        favorite, created = Favorite.objects.get_or_create(
            user=user, recipe=recipe
        )
        if not created:
            raise ValidationError({"errors": "Рецепт уже есть в избранном."})
        return favorite

    def _remove_from_favorite(self, user, recipe):
        favorite = user.favorites.filter(recipe=recipe)
        if not favorite.exists():
            raise ValidationError({"errors": "Рецепта нет в избранном."})
        favorite.delete()

    def _add_to_shopping_cart(self, user, recipe):
        shopping_cart = get_object_or_404(ShoppingCart, user=user)
        if recipe in shopping_cart.recipes.all():
            raise ValidationError(
                {"errors": "Рецепт уже есть в списке покупок."}
            )
        shopping_cart.recipes.add(recipe)

    def _remove_from_shopping_cart(self, user, recipe):
        shopping_cart = get_object_or_404(ShoppingCart, user=user)
        if recipe not in shopping_cart.recipes.all():
            raise ValidationError({"errors": "Рецепта нет в списке покупок."})
        shopping_cart.recipes.remove(recipe)

    def _get_shopping_cart_ingredients(self, shopping_cart):
        return (
            RecipeIngredient.objects.filter(
                recipe__shopping_carts=shopping_cart
            )
            .values(
                name=F("ingredient__name"),
                unit=F("ingredient__measurement_unit"),
            )
            .annotate(quantity=Sum("amount"))
            .order_by("name")
        )

    def _generate_ingredients_content(self, ingredients):
        return "\n".join(
            f"{item['name']} ({item['unit']}) — {item['quantity']}"
            for item in ingredients
        )

    def _create_canvas_and_textobject(self, buffer, pagesize):
        pdf_canvas = canvas.Canvas(buffer, pagesize=pagesize)
        textobject = pdf_canvas.beginText()
        return pdf_canvas, textobject

    def _draw_underline(
        self,
        pdf_canvas,
        width,
        x1_position,
        y1_position,
        x2_position,
        y2_position,
    ):
        pdf_canvas.setLineWidth(width)
        pdf_canvas.line(x1_position, y1_position, x2_position, y2_position)

    def _draw_text_line(
        self, textobject, font_name, font_size, text, x_position, y_position
    ):
        textobject.setTextOrigin(x_position, y_position)
        textobject.setFont(font_name, font_size)
        textobject.textLine(text)
        return textobject

    def _draw_content(
        self, textobject, font_name, font_size, text, x_position, y_position
    ):
        textobject.setTextOrigin(x_position, y_position)
        textobject.setFont(font_name, font_size)
        lines = text.split("\n")
        for line in lines:
            textobject.textLine(line)

        return textobject

    def _finalize_document(self, pdf_canvas, textobject, buffer):
        pdf_canvas.drawText(textobject)
        pdf_canvas.showPage()
        pdf_canvas.save()
        buffer.seek(0)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(
                Q(name__istartswith=name) | Q(name__icontains=name)
            )
            queryset = queryset.order_by(
                Case(
                    When(name__istartswith=name, then=0),
                    When(name__icontains=name, then=1),
                ),
                "name",
            )
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
