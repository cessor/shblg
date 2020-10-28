from django.urls import path
from django.views.generic import ListView, DetailView
from django.views.generic import ArchiveIndexView
from . import models

app_name = 'blog'

urlpatterns = [
    path(
        route='thema',
        view=ListView.as_view(
            model=models.Tag,
            context_object_name='tags'
        ),
        name='tags'
    ),
    path(
        route='thema/<slug:slug>',
        view=DetailView.as_view(
            model=models.Tag,
            context_object_name='tag'
        ),
        name='tag'
    ),
    path(
        route='author/',
        view=ListView.as_view(
            model=models.Author,
            context_object_name='authors'
        ),
        name='authors'
    ),
    path(
        route='author/<int:pk>',
        view=DetailView.as_view(
            model=models.Author,
            context_object_name='author'
        ),
        name='author'
    ),
    path(
        route='archiv',
        view=ArchiveIndexView.as_view(
            model=models.Article,
            date_field='published',
        ),
        name='archive'
    ),
    path(
        route='<slug:slug>',
        view=DetailView.as_view(
            model=models.Article,
            context_object_name='article'
        ),
        name='article'
    ),
    path(
        route='',
        view=ListView.as_view(
            model=models.Article,
            context_object_name='articles'
        ),
        name='index'
    ),
]
