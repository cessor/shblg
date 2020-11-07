from django.test import TestCase

from blog.models import Article

class ArticleTests(TestCase):
    def test_article_word_count(self):
        # System under Test
        article = Article.objects.create(
            title='Creating a Binary Search in Python',
            content='Lorem Ipsum'
        )

        # Act, Assert
        self.assertEqual(article.word_count, 2)
