from django.test import TestCase
from blog.models import Author


class AuthorTests(TestCase):
    def test_author_absolute_url_contains_username(self):
        # Arrange, System under Test
        author = Author.objects.create(
            username='johannes',
            first_name='Johannes',
            last_name='Hofmeister'
        )

        # Act
        url = author.get_absolute_url()

        # Assert
        self.assertEqual(url, '/author/johannes')

    def test_author_page(self):
        # Arrange, System under Test
        author = Author.objects.create(
            username='johannes',
            first_name='Johannes',
            last_name='Hofmeister',
            biography='Hello, World!'
        )

        # Act
        response = self.client.get(author.get_absolute_url())

        # Assert: Name on page
        self.assertInHTML(
            '<h1>Johannes</h1>',
            response.content.decode('utf-8')
        )

        # Assert: Bio on page
        self.assertInHTML(
            '<p>Hello, World!</p>',
            response.content.decode('utf-8')
        )
