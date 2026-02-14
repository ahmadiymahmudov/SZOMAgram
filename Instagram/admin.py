from django.contrib import admin

import Instagram.models as models
# Register your models here.

@admin.register(models.CustomUser)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("first_name",)
    list_display = ("id", "first_name","last_name","username", "email")
    list_display_links = ("id", "first_name")


@admin.register(models.Posts)
class CategoryPost(admin.ModelAdmin):
    search_fields = ("owner",)
    list_display = ("id", "owner","text")
    list_display_links = ("id", "owner")

@admin.register(models.Comment)
class CategoryComment(admin.ModelAdmin):
    search_fields = ("owner",)
    list_display = ("id", "owner","comment")
    list_display_links = ("id", "owner")


@admin.register(models.Saved_posts)
class CategorySaved(admin.ModelAdmin):
    search_fields = ("owner",)
    list_display = ("id", "owner","posts")
    list_display_links = ("id", "owner")