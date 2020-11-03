from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path(
        route='admin/doc/',
        view=include(
            'django.contrib.admindocs.urls'
        )
    ),
    path(
        route='admin/',
        view=admin.site.urls
    ),
    path(
        route='',
        view=include(
            'blog.urls',
            namespace='blog'
        )
    )
]
