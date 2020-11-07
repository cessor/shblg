from django.contrib.sitemaps import (GenericSitemap as GenericSitemapBase,
                                     Sitemap as SitemapBase)
from django.urls import reverse
from . import models


class ChangeFreq:
    """
    https://www.sitemaps.org/de/protocol.html#changefreqdef
    """
    always = 'always'
    hourly = 'hourly'
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'
    yearly = 'yearly'
    never = 'never'


class StaticViewSitemap(SitemapBase):
    """
    # https://docs.djangoproject.com/en/3.1/ref/contrib/sitemaps/#sitemap-for-static-views
    """

    name = ''

    def items(self):
        return [self.name]

    # pylint: disable=arguments-differ
    def location(self, item):
        return reverse(item)


class GenericSitemap(GenericSitemapBase):
    """
    Allows for static configuration of GenericSitemap-Objects
    """
    priority = 0.5
    date_field = '' # type: ignore

    def __init__(self):
        super().__init__(
            info_dict={
                'queryset': self.queryset,
                'date_field': self.date_field,
            },
            priority=self.priority
        )


class Sitemaps:
    """
    https://docs.djangoproject.com/en/3.1/ref/contrib/sitemaps/
    """
    class Index(StaticViewSitemap):
        changefreq = ChangeFreq.weekly
        priority = 0.9
        name = 'blog:index'

    class Archive(StaticViewSitemap):
        changefreq = ChangeFreq.weekly
        priority = 0.1
        name = 'blog:archive'

    class Authors(StaticViewSitemap):
        changefreq = ChangeFreq.yearly
        priority = 0.2
        name = 'blog:authors'

    class Tags(StaticViewSitemap):
        changefreq = ChangeFreq.monthly
        priority = 0.1
        name = 'blog:tags'

    class Article(GenericSitemap):
        changefreq = ChangeFreq.never
        priority = 0.8
        queryset = models.Article.objects.published()
        date_field = 'published'

    class Author(GenericSitemap):
        changefreq = ChangeFreq.yearly
        priority = 0.2
        queryset = models.Author.objects.all()
        date_field = 'updated'

    class Tag(GenericSitemap):
        changefreq = ChangeFreq.monthly
        priority = 0.1
        queryset = models.Tag.with_articles.all()
        date_field = 'created'

    def __iter__(self):
        # Return all members of the SitmapType
        for item in dir(self):
            member = getattr(self, item)
            if isinstance(member, type) and issubclass(member, SitemapBase):
                yield (member.__name__, member())
