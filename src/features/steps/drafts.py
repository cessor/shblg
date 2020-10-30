from typing import Tuple
from behave import given, when, then
from django.test import RequestFactory
from django.urls import reverse, resolve


def goto_page(context, route: str):
    url = reverse(route)
    request = context.requests.get(url)
    request.user = context.author
    view = resolve(url).func
    response = view(request)
    return response.render()


@given(u'I am an author')
def i_am_an_author(context):
    from blog.models import Author, Article
    author, created = Author.objects.get_or_create(
        username='carl.rogers',
        email='carl@example.com'
    )
    context.author = author


@given(u'I have logged in')
def log_in(context):
    context.requests = RequestFactory()


@when(u'I am writing and article')
def write_an_article(context):
    from blog.models import Author, Article
    article, *_ = context.table
    context.article = Article.objects.create(
        title=article.get('Title'),
        content=article.get('Content')
    )


@when(u'I set the published date to None')
def set_publish_date_to_none(context):
    # Published will default to timezone.now, if left alone
    context.article.published = None
    context.article.save()


@then(u'I the article becomes a draft')
def article_is_found_in_drafts(context):
    from blog.models import Author, Article
    context.test.assertIn(
        context.article,
        Article.drafts.all(),
    )

    context.test.assertIn(
        context.article,
        Article.objects.all(),
    )


@given(u'I have written a draft')
def write_a_draft(context):
    from blog.models import Author, Article
    article = Article.objects.create(
        title='Hello, World!',
        content='',
        published=None,
    )
    article.authors.add(context.author)
    article.save()


@when(u'I am on the index page')
def go_to_index_page(context):
    context.response = goto_page(context, 'blog:index')


@then(u'I can see a menu item that leads me to the drafts page')
def look_at_menu_items(context):
    context.test.assertInHTML(
        '''<a href="/entwurf">Entwürfe</a>''',
        context.response.content.decode('utf-8')
    )


@when(u'I am on the drafts page')
def go_to_drafts_page(context):
    context.response = goto_page(context, 'blog:drafts')


@then(u'I can see the draft')
def step_impl(context):
    context.test.assertInHTML(
        '''<h1><a href="/entwurf/hello-world">Hello, World!</a></h1>''',
        context.response.content.decode('utf-8')
    )


@given(u'somebody else has written a draft')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given somebody else has written a draft')


@then(u'I can\'t see that draft')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I can\'t see that draft')


@then(u'I can inspect the draft')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I can inspect the draft')


@when(u'I am inspecting the draft')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I am inspecting the draft')


@then(u'I am notified that it has not yet been published')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then I am notified that it has not yet been published')


@given(u'I view a draft')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given I view a draft')


@then(u'I am offered to publish it right away')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then I am offered to publish it right away')


@given(u'I am not logged in')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given I am not logged in')


@then(u'I don\'t see a menu item for drafts')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then I don\'t see a menu item for drafts')


@when(u'I try accessing the drafts page')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I try accessing the drafts page')


@then(u'I am asked to login')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I am asked to login')


@when(u'I try inspecting a specific draft')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I try inspecting a specific draft')
