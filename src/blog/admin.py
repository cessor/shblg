from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


@admin.register(models.Author)
class AuthorAdmin(UserAdmin):
    def has_pgp_key(self, instance):
        return not not instance.pgp_public_key
    has_pgp_key.boolean = True

    fieldsets = UserAdmin.fieldsets + ((
        'PGP', {
            'fields': ('pgp_public_key',)
        }),  # Don't change these commas
    )

    list_display = UserAdmin.list_display + ('has_pgp_key',)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    def author_display(self, instance):
        return ', '.join(
            str(author) for author in instance.authors.all()
        )

    search_fields = ['title']

    list_filter = ['authors', 'tags', 'created', 'updated']

    list_display = ['title', 'author_display', 'created', 'updated']
