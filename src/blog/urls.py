from django.urls import path
from django.views.generic import ListView, DetailView

from . import models

app_name = 'blog'

urlpatterns = [
    path(
        route='tag',
        view=ListView.as_view(
            model=models.Tag,
            context_object_name='tags'
        ),
        name='tags'
    ),
    path(
        route='tag/<slug:slug>',
        view=DetailView.as_view(
            model=models.Tag,
            context_object_name='tag'
        ),
        name='tag'
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
