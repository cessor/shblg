from django.contrib.sites.shortcuts import get_current_site
def site(request):
    print(request.method)
    return {'SITE': get_current_site(request)}