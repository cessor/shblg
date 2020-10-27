from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.apps import AuthConfig
from django.db import models
from django.utils.text import slugify as slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Sluggable:
    SLUGIFY_FIELD = ''

    def slugify_german(self, text):
        # Ugly. How else?
        text = text.replace('ä', 'ae')
        text = text.replace('ö', 'oe')
        text = text.replace('ü', 'ue')
        text = text.replace('ß', 'ss')
        return slugify(text)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.slugify_german(getattr(self, self.SLUGIFY_FIELD))
        super().save(*args, **kwargs)


class Author(AbstractUser):
    pgp_public_key = models.TextField(
        verbose_name=_('Öffentlicher PGP-Schlüssel'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Autor')
        verbose_name_plural = _('Autoren')


class Color:

    COLORS = [
        "red",
        "orange",
        "yellow",
        "olive",
        "green",
        "teal",
        "blue",
        "violet",
        "purple",
        "pink",
        "brown",
        "black",
    ]

    class Hash(object):
        """
        Source
        https://stackoverflow.com/a/33810066
        """

        def __init__(self, string, domain):
            self._string = string
            self._domain = domain

        def __int__(self):
            return sum(map(lambda c: ord(c) ** 2, self._string)) % self._domain

    def __init__(self, color):
        self._color = color

    def __str__(self):
        return self._color

    @classmethod
    def from_string(cls, string):
        hash = Color.Hash(string, domain=len(Color.COLORS))
        index = int(hash)
        return cls(Color.COLORS[index])


class Tag(Sluggable, models.Model):
    SLUGIFY_FIELD = 'tag'

    tag = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        unique=True
    )

    slug = models.SlugField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        help_text=_('Freilassen, um Slug aus dem Titel zu generieren')
    )

    def color(self):
        return Color.from_string(self.tag)

    def get_absolute_url(self):
        return reverse('blog:tag', args=[self.slug])

    def __str__(self):
        return str(self.tag)


class Article(Sluggable, models.Model):
    SLUGIFY_FIELD = 'title'

    site = models.ForeignKey(
        to='sites.Site',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        default=settings.SITE_ID
    )

    title = models.CharField(
        verbose_name=_('Titel'),
        max_length=255,
    )

    slug = models.SlugField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        help_text=_('Freilassen, um Slug aus dem Titel zu generieren')
    )

    content = models.TextField(
        verbose_name=_('Inhalt'),
        help_text=_('Unterstützt Markdown-Syntax')
    )

    authors = models.ManyToManyField(
        Author,
        verbose_name=_('Autoren'),
        related_name='articles',
        blank=True
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('Tags'),
        related_name='articles',
        blank=True
    )

    published = models.DateTimeField(
        verbose_name=_('Veröffentlicht am'),
        null=True,
        blank=True,
        default=timezone.now
    )

    created = models.DateTimeField(
        verbose_name=_('Erstellt am'),
        auto_now_add=True
    )

    updated = models.DateTimeField(
        verbose_name=_('Geändert am'),
        auto_now=True
    )

    def get_absolute_url(self):
        return reverse('blog:article', args=[self.slug])

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = _('Artikel')
        verbose_name_plural = _('Artikel')
