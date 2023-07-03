from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignUpView,
    TitleViewSet,
    TokenView,
    UserViewSet
)


router_v1 = DefaultRouter()
router_v1.register(r"users", UserViewSet, basename="user")
router_v1.register(r"genres", GenreViewSet, basename="genre")
router_v1.register(r"categories", CategoryViewSet, basename="category")
router_v1.register(r"titles", TitleViewSet, basename="title")
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews",
    ReviewViewSet,
    basename="reviews"
)
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments"
)

auth_patterns = [
    path("signup/", SignUpView.as_view()),
    path("token/", TokenView.as_view()),
]

urlpatterns = [
    path("v1/", include(router_v1.urls)),
    path("v1/auth/", include(auth_patterns))
]
