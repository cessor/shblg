from django.contrib.sites.shortcuts import get_current_site
from blog.models import Article


def site(request):
    return {'SITE': get_current_site(request)}


def anonymous_drafts(request):
    """
    If there are drafts,
    an additional menu item should be displayed. This function
    finds out if there are any anonymous drafts, i.e. drafts without an
    authors set.
    """
    return {
        'anonymous_drafts': Article.drafts.anonymous().count() > 0
    }
