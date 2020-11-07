import re
from bs4 import BeautifulSoup
from django.test import TestCase
from blog.models import Author, Article


def collapse_whitespace(text):
    pattern = re.compile(r'\s+')
    return pattern.sub(' ', text).strip()


class ArticleTests(TestCase):
    def test_one_author(self):
        # Arrange: Authors
        lars = Author.objects.create(
            username='larscov2',
            first_name='Lars'
        )

        # Arrange: Article
        article = Article.objects.create(
            title='Creating a Binary Search in Python',
            content='Lorem Ipsum'
        )

        # Arrange: Add Authorship
        article.authors.add(lars)
        article.save()

        # Act, System under Test
        response = self.client.get(article.get_absolute_url())

        soup = BeautifulSoup(response.content, 'lxml')
        authors = soup.find('span', attrs={'class': 'authors'})
        authors = collapse_whitespace(authors.text)

        # Assert: Authors are listed correctly
        self.assertEqual(
            authors,
            'Geschrieben von Lars.'
        )

    def test_two_authors(self):
        # Arrange: Authors
        lars = Author.objects.create(
            username='larscov2',
            first_name='Lars'
        )

        horst = Author.objects.create(
            username='shorst',
            first_name='Horst'
        )

        # Arrange: Article
        article = Article.objects.create(
            title='Creating a Binary Search in Python',
            content='Lorem Ipsum'
        )

        # Arrange: Add Authorship
        article.authors.add(lars)
        article.authors.add(horst)
        article.save()

        # Act, System under Test
        response = self.client.get(article.get_absolute_url())

        soup = BeautifulSoup(response.content, 'lxml')
        authors = soup.find('span', attrs={'class': 'authors'})
        authors = collapse_whitespace(authors.text)

        # Assert: Authors are listed correctly
        self.assertEqual(
            authors,
            'Geschrieben von Horst und Lars.'
        )

    def test_more_than_two_authors(self):
        # Arrange: Authors
        lars = Author.objects.create(
            username='larscov2',
            first_name='Lars'
        )

        horst = Author.objects.create(
            username='shorst',
            first_name='Horst'
        )

        johannes = Author.objects.create(
            username='hjohannes',
            first_name='Johannes'
        )

        # Arrange: Article
        article = Article.objects.create(
            title='Creating a Binary Search in Python',
            content='Lorem Ipsum'
        )

        # Arrange: Add Authorship
        article.authors.add(lars)
        article.authors.add(horst)
        article.authors.add(johannes)
        article.save()

        # Act, System under Test
        response = self.client.get(article.get_absolute_url())

        soup = BeautifulSoup(response.content, 'lxml')
        authors = soup.find('span', attrs={'class': 'authors'})
        authors = collapse_whitespace(authors.text)

        # Assert: Authors are listed correctly
        self.assertEqual(
            authors,
            'Geschrieben von Horst, Johannes und Lars.'
        )
