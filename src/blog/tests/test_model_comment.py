from django.test import TestCase
from blog.models import Article, Author, Comment

class CommentTests(TestCase):
    def test_comment(self):
        writer = Author.objects.create(
            username='Horst',
        )

        commenter = Author.objects.create(
            username='Johannes'
        )

        Article.objects.create(

        )

