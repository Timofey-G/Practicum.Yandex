from django.contrib import admin

from users.models import CustomUser

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "created", "author", "group")
    list_editable = ("group",)
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "post", "created", "author")
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow)
admin.site.register(CustomUser)
