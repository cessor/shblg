from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import RedirectView
from django.views.generic import DetailView, ListView
from django.db.models import Q
from django.utils import timezone
from . import models


class DraftView(PermissionRequiredMixin, DetailView):
    """
    Displays a draft.
    """
    permission_required = 'blog.view_draft'
    model = models.Article
    context_object_name = 'article'


class DraftsView(PermissionRequiredMixin, ListView):
    """
    Displays drafts (i.e. articles without a ```published``` date)
    """
    permission_required = 'blog.publish_draft'
    model = models.Article
    context_object_name = 'articles'

    def get_queryset(self):
        """
        Returns drafts for the current user.
        Anonymous drafts are included.
        """
        return models.Article.drafts.filter(
            Q(authors__in=[self.request.user]) | Q(authors=None)
        )


class PublishDraftView(
        PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    """
    Action: Publishes a draft by setting its published date to
    the current date and time. This works for drafts, i.e. unpublished
    articles. If it is activated for a published article, nothing happens
    because the article has already been published.

    The view redirects to articles final, published view.
    """
    permission_required = 'blog.publish_draft'
    model = models.Article

    def get_redirect_url(self, *args, **kwargs):
        """
        Accesses a draft and publishes it. The user is redirected to
        the published article. If the requested article is already
        published, nothing happens and the user is redirected to the article.
        """
        draft = self.get_object()
        if not draft.published:
            draft.published = timezone.now()
            draft.save()
        return draft.get_absolute_url()
