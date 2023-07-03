from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(
        "Фото профиля",
        upload_to="users/",
        blank=True,
        null=True,
        help_text="Загрузите фото профиля",
    )
