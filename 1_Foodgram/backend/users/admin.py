from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Favorite, Follow, ShoppingCart

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email")
    list_filter = ("username", "email")


admin.site.register(Favorite)
admin.site.register(Follow)
admin.site.register(ShoppingCart)
