from django.test import TestCase
from blog.models import Article, Author, Comment

class CommentTests(TestCase):
    def test_comment(self):
        # Arrange
        writer = Author.objects.create(
            username='Horst',
        )

        commenter = Author.objects.create(
            username='Johannes'
        )

        article = Article.objects.create(
            title='Rich comparisons',
            content=(
                'An integral part of what makes Python awesome is that you '
                'can customize almost every aspect of the interaction between '
                'your objects and the Python ecosystem. '
            )
        )

        article.authors.add(writer)
        article.save()

        # Act, System under Test
        comment = Comment.objects.create(
            article=article,
            content='This needs some work',
            author=commenter
        )

        # Assert: Date set
        self.assertTrue(comment.created)
        self.assertTrue(comment.updated)
        self.assertFalse(comment.accepted)