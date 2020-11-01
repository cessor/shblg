from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin

from . import models


@admin.register(models.Author)
class AuthorAdmin(UserAdmin):
    def has_pgp_key(self, instance):
        return not not instance.pgp_public_key
    has_pgp_key.boolean = True
    has_pgp_key.short_description = _('PGP-Key Hinterlegt?')

    readonly_fields = ['updated']
    # Don't change these commas
    fieldsets = (
        (
            _('Biografie'), {'fields': ('biography', 'updated')}
        ),
        (
            _('PGP'), {'fields': ('pgp_public_key',)}
        ),
    ) + UserAdmin.fieldsets

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(username=request.user.username)

    def get_form(self, request, obj=None, **kwargs):
        # Source:
        # https://realpython.com/manage-users-in-django-admin/
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        # Disable all fields
        disabled_fields = [
            field.name for field in models.Author._meta.fields
        ] + ['groups', 'user_permissions', ]

        # Superusers can do whatevery they want
        if is_superuser:
            disabled_fields = []

        # Enable editing personal data
        if (
            not is_superuser
            and obj is not None
            and obj == request.user
        ):
            disabled_fields.remove('biography')
            disabled_fields.remove('email')
            disabled_fields.remove('first_name')
            disabled_fields.remove('last_name')
            disabled_fields.remove('pgp_public_key')

        # Disable all fields
        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True

        return form


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

    list_filter = ['authors', 'published', 'created', 'updated', 'tags']

    list_display = ['title', 'author_display', 'published',
                    'created', 'updated', 'site']
