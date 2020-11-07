from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import ListView, DetailView
from django.views.generic import ArchiveIndexView, TemplateView

from . import views
from .models import Article, Author, Tag
from .sitemaps import Sitemaps

app_name = 'blog' # pylint: disable=invalid-name

urlpatterns = [
    path(
        route='robots.txt',
        view=TemplateView.as_view(
            template_name='blog/robots.txt',
            content_type='text/plain'
        ),
        name='robots'
    ),
    path(
        route='sitemap.xml',
        view=sitemap,
        kwargs={'sitemaps': dict(Sitemaps())},
        name='django.contrib.sitemaps.views.sitemap'
    ),
    path(
        route='author/',
        view=ListView.as_view(
            model=Author,
            context_object_name='authors'
        ),
        name='authors'
    ),
    path(
        route='author/<slug:slug>',
        view=DetailView.as_view(
            model=Author,
            context_object_name='author',
            slug_field='username'
        ),
        name='author'
    ),
    path(
        route='archiv',
        view=ArchiveIndexView.as_view(
            model=Article,
            date_field='published',
            allow_empty=True
        ),
        name='archive'
    ),
    path(
        route='entwurf/<slug:slug>',
        view=views.DraftView.as_view(),
        name='draft'
    ),
    path(
        route='entwurf/<slug:slug>/publish',
        view=views.PublishDraftView.as_view(),
        name='publish_now'
    ),
    path(
        route='entwurf',
        view=views.DraftsView.as_view(),
        name='drafts'
    ),
    path(
        route='thema',
        view=ListView.as_view(
            model=Tag,
            get_queryset=Tag.with_articles.all,
            context_object_name='tags'
        ),
        name='tags'
    ),
    path(
        route='thema/<slug:slug>',
        view=DetailView.as_view(
            model=Tag,
            context_object_name='tag'
        ),
        name='tag'
    ),
    path(
        route='<slug:slug>',
        view=DetailView.as_view(
            model=Article,
            context_object_name='article'
        ),
        name='article'
    ),
    *static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    ),
    path(
        route='',
        view=ListView.as_view(
            model=Article,
            context_object_name='articles',
            get_queryset=Article.chronological.all
        ),
        name='index'
    ),
]
