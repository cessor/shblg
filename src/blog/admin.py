from django import forms
from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from . import models


class PreviewWidget(admin.widgets.AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs, renderer)
        if not value:
            return input_html

        return format_html(
            '{}<br><img src="{}">',
            input_html, value.url
        )


class AuthorAdminForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['portrait'].widget = PreviewWidget()


@admin.register(models.Author)
class AuthorAdmin(UserAdmin):
    form = AuthorAdminForm

    def has_pgp_key(self, instance):
        return instance.pgp_public_key

    has_pgp_key.boolean = True
    has_pgp_key.short_description = _('PGP-Key Hinterlegt?')

    readonly_fields = ['updated', 'last_login', 'date_joined']

    fieldsets = (
        # Don't change these commas
        # These values were adopted from the original django admin fieldsets
        # This is a static copy, which is brittle, i.e. it might break
        # if the default fieldsets in the user admin change.
        #
        # While it is possible to change the fieldsets by overrider
        # UserAdmin.get_fieldsets(self, request, instance, **kwargs)
        # Changing this structure procedurally makes for some hard-to-read
        # code, this I cloned the structure.
        #
        # https://github.com/django/django/blob/master/django/contrib/auth/admin.py#L44
        (
            None,
            {
                'fields': ('username', 'password')
            }
        ),
        (
            _('Personal info'),
            {
                'fields': (
                    'first_name', 'last_name', 'email',
                    'portrait', 'biography'
                )
            }
        ),
        (
            _('PGP'), {'fields': ('pgp_public_key',)}
        ),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            }
        ),
        (
            _('Important dates'),
            {
                'fields': ('updated', 'last_login', 'date_joined')
            }
        ),
    )


    def get_fieldsets(self, request, obj=None):
        """
        Removes Permission fieldset for normal users.
        """
        fieldsets = dict(super().get_fieldsets(request, obj))
        if not request.user.is_superuser:
            del fieldsets[_('Permissions')]
        return tuple(fieldsets.items())

    def get_queryset(self, request):
        """
        Limits the changable users to the current user.
        Unless they're superusers, then they can do whatever.
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(
            username=request.user.username
        )

    def get_form(self, request, obj=None, **kwargs):
        """
        Disables some fields for normal users.
        """
        # Source:
        # https://realpython.com/manage-users-in-django-admin/
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        # Disable all fields
        # pylint: disable=no-member,protected-access
        disabled_fields = (
            [field.name for field in models.Author._meta.fields]
            + ['groups', 'user_permissions']
        )

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
            disabled_fields.remove('portrait')
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


class ImageForm(forms.ModelForm):
    image = forms.ImageField(
        widget=PreviewWidget
    )

    class Meta:
        model = models.Image
        fields = ['title', 'image']


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    def thumbnail(self, instance):
        return format_html(
            '<img class="thumbnail" src="{image}" title="{title}">',
            image=instance.image.url,
            title=instance.title
        )

    def resolution(self, instance):
        if not instance.image:
            return '-'
        return f'{instance.width} x {instance.height}'

    form = ImageForm

    search_fields = ['title']

    list_filter = ['created', 'updated']

    list_display = ['thumbnail', 'title', 'created', 'updated']

    list_display_links = ['thumbnail', 'title']

    readonly_fields = ['resolution', 'width', 'height', 'created', 'updated']

    class Media:
        css = {
            'all': ('blog/image_admin.css', )
        }
