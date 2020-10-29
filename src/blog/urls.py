from django.urls import path
from django.views.generic import ListView, DetailView
from django.views.generic import ArchiveIndexView, TemplateView
from .models import Article, Author, Tag

app_name = 'blog'


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
        route='author/',
        view=ListView.as_view(
            model=Author,
            context_object_name='authors'
        ),
        name='authors'
    ),
    path(
        route='author/<int:pk>',
        view=DetailView.as_view(
            model=Author,
            context_object_name='author'
        ),
        name='author'
    ),
    path(
        route='archiv',
        view=ArchiveIndexView.as_view(
            model=Article,
            date_field='published',
            allow_empty = True
        ),
        name='archive'
    ),
    path(
        route='<slug:slug>',
        view=DetailView.as_view(
            model=Article,
            context_object_name='article'
        ),
        name='article'
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
