import re
import textwrap
from django.conf import settings
from django.contrib.auth.apps import AuthConfig
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify as slugify
from django.utils.translation import gettext_lazy as _

import mistune


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

    biography = models.TextField(
        verbose_name=_('Biografie'),
        null=True,
        blank=True,
        help_text=_('Unterstützt Markdown-Syntax')
    )

    updated = models.DateTimeField(
        verbose_name=_('Geändert am'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Autor')
        verbose_name_plural = _('Autoren')
        ordering = ['first_name']

    def get_absolute_url(self):
        return reverse('blog:author', args=[self.id])


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


class TaggedArticleManager(models.Manager):
    def get_queryset(self):
        """
        Retrieves all tags with articles that have actually
        been published. This prevents empty tags from appearing
        on the tags page.
        """
        return (
            super()
            .get_queryset()
            .annotate(
                n_articles=models.Count(
                    'articles',
                    filter=models.Q(
                        articles__published__isnull=False
                    )
                )
            )
            .filter(n_articles__gt=0)
        )


class Tag(Sluggable, models.Model):
    objects = models.Manager()
    with_articles = TaggedArticleManager()

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

    created = models.DateTimeField(
        auto_now_add=True
    )

    def color(self):
        return Color.from_string(self.tag)

    def get_absolute_url(self):
        return reverse('blog:tag', args=[self.slug])

    def __str__(self):
        return str(self.tag)


class PublishedArticlesManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(published__isnull=False)
            .order_by('-published')
        )


class ChronologicalManager(PublishedArticlesManager):
    def get_queryset(self):
        return super().get_queryset().order_by('-published')


class DraftsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            published__isnull=True
        )

    def anonymous(self):
        return self.get_queryset().filter(authors=None)


class ArticleQuerySet(models.QuerySet):
    def drafts(self):
        return self.filter(published__isnull=True)

    def published(self):
        return self.filter(published__isnull=False)


class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def drafts(self):
        return self.get_queryset().drafts()

    def published(self):
        return self.get_queryset().published()


class Article(Sluggable, models.Model):
    objects = ArticleManager()
    drafts = DraftsManager()
    published_articles = PublishedArticlesManager()
    chronological = ChronologicalManager()
    on_site = CurrentSiteManager()

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

    created = models.DateTimeField(
        verbose_name=_('Erstellt am'),
        auto_now_add=True
    )

    updated = models.DateTimeField(
        verbose_name=_('Geändert am'),
        auto_now=True
    )

    published = models.DateTimeField(
        verbose_name=_('Veröffentlicht am'),
        null=True,
        blank=True,
        default=timezone.now
    )

    @property
    def summary(self):
        html = mistune.markdown(str(self.content))
        text_without_breaks = ''.join(
            (c if c not in '\n\r\t' else ' ')
            for c in re.sub(r'<(.*?)>', '', html).strip()
        )
        return textwrap.shorten(
            text_without_breaks,
            width=255,
            placeholder='...'
        )

    def get_absolute_url(self):
        if self.published:
            return reverse('blog:article', args=[self.slug])
        return reverse('blog:draft', args=[self.slug])

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = _('Artikel')
        verbose_name_plural = _('Artikel')

        permissions = (
            ("view_draft", _("Can view draft")),
            ("publish_draft", _("Can publish draft")),
        )
