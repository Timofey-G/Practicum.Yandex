from random import choices

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filter
from rest_framework import (
    filters,
    mixins,
    serializers,
    status,
    views,
    viewsets
)
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    IsAdmin,
    IsAdminModerAuthorOrReadOnly,
    IsAdminOrReadOnly,
)
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleCreateUpdateSerializer,
    TitleSerializer,
    TokenSerializer,
    UserSerializer,
)
from reviews.models import Category, Genre, Review, Title, User


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "delete", "patch")
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == "GET":
            return Response(self.get_serializer(request.user).data)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)


class SignUpView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        username = serializer.validated_data["username"]
        try:
            user, _ = User.objects.get_or_create(
                email=email,
                username=username,
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {"message": "Пользователь с такими данными уже существует"}
            )
        user.confirmation_code = "".join(
            choices(settings.ACCESSIBLE_CHARS, k=settings.CODE_LENGTH)
        )
        user.save(update_fields=["confirmation_code"])
        send_mail(
            subject="Confirmation Code",
            message=f"Ваш код активации: {user.confirmation_code}",
            recipient_list=[email],
            from_email=settings.EMAIL_HOST_USER,
        )
        return Response(serializer.data)


class TokenView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data["confirmation_code"]
        username = serializer.validated_data["username"]
        user = get_object_or_404(User, username=username)
        if (
            user.confirmation_code == settings.INTRUDER_STOPPER
        ):
            return Response(
                {"message": "Код подтверждения недействителен"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if (user.confirmation_code != confirmation_code):
            user.confirmation_code = settings.INTRUDER_STOPPER
            user.save(update_fields=["confirmation_code"])
            return Response(
                {"message": "Неверный код подтверждения"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.confirmation_code = settings.INTRUDER_STOPPER
        user.save(update_fields=["confirmation_code"])
        token = AccessToken.for_user(user)
        return Response({"Bearer": f"{token}"})


class GenreCategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "slug"
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class GenreViewSet(GenreCategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(GenreCategoryViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "delete", "patch")
    queryset = Title.objects.all().annotate(rating=Avg("reviews__score"))
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (
        filter.DjangoFilterBackend,
        filters.OrderingFilter
    )
    filterset_class = TitleFilter
    ordering_fields = ("year", "name")
    ordering = ("-year", "name")

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return TitleCreateUpdateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModerAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(title=self.get_title(), author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModerAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get("review_id"),
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(), author=self.request.user)
