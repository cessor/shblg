from typing import Tuple
from behave import given, when, then
from django.core.exceptions import PermissionDenied
from django.test import Client, RequestFactory
from django.urls import reverse, resolve


def goto_page(context, route: str, args=None, request_kwargs=None):
    args = args or []
    request_kwargs = request_kwargs or {}
    url = reverse(route, args=args)
    request = context.requests.get(url)
    request.user = context.author
    view = resolve(url).func
    response = view(request, **request_kwargs)
    try:
        return response.render()
    except AttributeError:
        # Redirects don't have .render()
        return response


@given(u'I am an author')
def i_am_an_author(context):
    from blog.models import Author
    author, created = Author.objects.get_or_create(
        username='carl.rogers',
        email='carl@example.com'
    )
    context.author = author


@given(u'I have permissions to view and publish drafts')
def permit_publishing_and_viewing_drafts(context):
    from blog.models import Article
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_model(Article)

    can_change_article = Permission.objects.get(
        content_type=content_type, codename='change_article'
    )
    context.author.user_permissions.add(can_change_article)

    can_view_draft = Permission.objects.get(
        content_type=content_type, codename='view_draft'
    )
    context.author.user_permissions.add(can_view_draft)

    can_publish_draft = Permission.objects.get(
        content_type=content_type, codename='publish_draft'
    )
    context.author.user_permissions.add(can_publish_draft)


@given(u'I have logged in')
def log_in(context):
    context.requests = RequestFactory()


@when(u'I am writing an article')
def write_an_article(context):
    from blog.models import Article
    context.article = Article.objects.create(
        title='On becoming a person',
        content="A Therapist's View of Psychotherapy"
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
    from blog.models import Article
    article = Article.objects.create(
        title='Hello, World!',
        content=(
            'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, '
            'sed diam nonumy eirmod tempor invidunt ut labore et dolore '
            'magna aliquyam erat, sed diam voluptua.'
        ),
        published=None,
    )
    article.authors.add(context.author)
    article.save()
    context.draft = article


@when(u'I am on the index page')
def go_to_index_page(context):
    context.response = goto_page(context, 'blog:index')


@then(u'I can see a menu item that leads me to the drafts page')
def look_at_menu_items(context):
    context.test.assertInHTML(
        '''<a href="/entwurf">Entwürfe</a>''',
        context.response.render().content.decode('utf-8')
    )


@then(u'I don\'t see the draft')
def step_impl(context):
    context.test.assertNotIn(
        '''Hello, World!''',
        context.response.content.decode('utf-8')
    )


@when(u'I am on the drafts page')
def go_to_drafts_page(context):
    context.response = goto_page(context, 'blog:drafts')


@then(u'I can see the draft')
def look_at_draft(context):
    context.test.assertInHTML(
        '''<h1><a href="/entwurf/hello-world">Hello, World!</a></h1>''',
        context.response.content.decode('utf-8')
    )


@given(u'somebody else has written a draft')
def someone_else_writes_a_draft(context):
    from blog.models import Author, Article

    author, created = Author.objects.get_or_create(
        # R.I.P., Peter F. Schmid, 1950 - 2020
        username='peter.schmid',
        email='peter.schmid@example.com'
    )

    draft = Article.objects.create(
        # http://www.pfs-online.at/1/seuche.pdf
        title="Wir kaufen Klopapier, damit wir uns nicht vor Angst anscheißen",
        content=(
            'Personzentrierte und persönliche Anmerkungen zu Angst und '
            'Hoffnung in Zeiten der Seuche - Reaktionen dazu'
        ),
        published=None,
    )

    draft.authors.add(author)
    draft.save()
    context.draft = draft


@then(u'I can\'t see that draft')
def look_at_draft_but_its_not_there(context):
    context.test.assertNotIn(
        context.draft.title,
        context.response.content.decode('utf-8')
    )


@given(u'an article without an author')
def create_an_article_without_an_author(context):
    from blog.models import Article
    anonymous_article = Article.objects.create(
        # http://pfs-online.at/1/papers/pp-budapest2019.pdf
        title='Orthodoxy? Mainstream? Evolution? Revolution?',
        content='Is the PCA still a therapeutic and societal counter-model?',
        published=None,
    )
    context.anonymous_article = anonymous_article


@then(u'I can see the anonymous draft')
def see_anonymous_draft(context):
    context.test.assertIn(
        context.anonymous_article.title,
        context.response.content.decode('utf-8')
    )


@then(u'I can see its content')
def inspect_the_draft(context):
    context.test.assertInHTML(
        '''<h1><a href="/entwurf/hello-world">Hello, World!</a></h1>''',
        context.response.content.decode('utf-8')
    )

    response = goto_page(
        context,
        'blog:draft',
        args=[context.draft.slug],
        request_kwargs=dict(slug=context.draft.slug)
    )

    context.test.assertEqual(
        response.status_code, 200
    )


@when(u'I am inspecting the draft')
def inspect_draft(context):
    context.response = goto_page(
        context,
        'blog:draft',
        args=[context.draft.slug],
        request_kwargs=dict(slug=context.draft.slug)
    )


@then(u'I am notified that it has not yet been published')
def look_at_notification(context):
    context.test.assertNotIn(
        'Veröffentlicht',
        context.response.content.decode('utf-8')
    )

    context.test.assertIn(
        'Dies ist ein Entwurf',
        context.response.content.decode('utf-8')
    )


@then(u'I am offered to publish it right away')
def look_at_publishing_note(context):
    context.test.assertInHTML(
        '<a href="/entwurf/hello-world/publish">jetzt veröffentlichen</a>',
        context.response.content.decode('utf-8')
    )


@given(u'I don\'t have the permissions to publish a draft')
def prohibit_publishing(context):
    from blog.models import Article
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    # Remove permission to publish draft
    # Note: This is true for each of these tests
    content_type = ContentType.objects.get_for_model(Article)
    context.author.user_permissions.remove(
        Permission.objects.get(
            content_type=content_type,
            codename='publish_draft'
        )
    )


@when(u'I publish it')
def publish_article(context):
    context.response = goto_page(
        context,
        'blog:publish_now',
        args=[context.draft.slug],
        request_kwargs=dict(slug=context.draft.slug)
    )


@when(u'I try to publish it')
def try_to_publish_article(context):
    with context.test.assertRaises(PermissionDenied):
        goto_page(
            context,
            'blog:publish_now',
            args=[context.draft.slug],
            request_kwargs=dict(slug=context.draft.slug)
        )


@then(u'the article is not published')
def assert_that_published_date_was_not_set(context):
    context.draft.refresh_from_db()
    context.test.assertFalse(
        context.draft.published
    )


@then(u'I am redirected to the published article')
def view_published_article_after_redirect(context):
    context.test.assertEqual(
        context.response.status_code,
        302
    )

    context.draft.refresh_from_db()

    context.test.assertEqual(
        context.response.url,
        context.draft.get_absolute_url()
    )


@given(u'I am not logged in')
def log_out(context):
    from django.contrib.auth.models import AnonymousUser
    context.author = AnonymousUser()


@then(u'I don\'t see a menu item for drafts')
def look_at_menu_but_item_is_not_there(context):
    context.test.assertNotIn(
        '''Entwürfe''',
        context.response.content.decode('utf-8')
    )


@when(u'I try accessing the drafts page')
def try_going_to_drafts_page(context):
    context.response = goto_page(
        context,
        'blog:drafts',
    )


@then(u'I am asked to login')
def assert_redirect_to_login_page(context):
    context.test.assertEqual(
        context.response.status_code, 302
    )
    context.test.assertIn(
        'login',
        context.response.url
    )


@when(u'I try inspecting a specific draft')
def try_inspecting_draft(context):
    from blog.models import Article
    draft = Article.objects.create(
        title='Hello, World!',
        content=(
            'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, '
            'sed diam nonumy eirmod tempor invidunt ut labore et dolore '
            'magna aliquyam erat, sed diam voluptua.'
        ),
        published=None,
    )

    context.response = goto_page(
        context,
        'blog:draft',
        args=[draft.slug],
        request_kwargs=dict(slug=draft.slug)
    )


@given(u'the draft is tagged')
def add_tags_to_draft(context):
    from blog.models import Tag
    tag = Tag.objects.create(
        tag="Example",
    )
    context.draft.tags.add(tag)
    context.draft.save()


@when(u'I am on the tags page')
def go_to_tags_page(context):
    context.response = goto_page(
        context,
        'blog:tags'
    )


@then(u'the article does not activate the tag')
def assert_tag_not_on_page(context):
    context.test.assertNotIn(
        'Example',
        context.response.content.decode('utf-8')
    )


@when(u'I am on my author page')
def go_to_author_page(context):
    client = Client()
    url = context.author.get_absolute_url()
    context.response = client.get(url)


@then(u'the draft does not appear in my list of articles')
def assert_draft_not_in_article_list(context):
    context.test.assertNotIn(
        context.draft.title,
        context.response.content.decode('utf-8')
    )

@given(u'an anonymous draft')
def create_anonymous_article(context):
    from blog.models import Article
    anonymous_article = Article.objects.create(
        # http://pfs-online.at/1/papers/pp-budapest2019.pdf
        title='Orthodoxy? Mainstream? Evolution? Revolution?',
        content='Is the PCA still a therapeutic and societal counter-model?',
        published=None,
    )
    context.anonymous_article = anonymous_article