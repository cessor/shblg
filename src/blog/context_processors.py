from django.contrib.sites.shortcuts import get_current_site
from blog.models import Article

def site(request):
    return {'SITE': get_current_site(request)}


def anonymous_drafts(request):
    print(Article.drafts.anonymous().count() > 0)
    return {'anonymous_drafts': Article.drafts.anonymous().count() > 0 }