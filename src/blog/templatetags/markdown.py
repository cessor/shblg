from django import template
from pygments import highlight
from pygments.formatters import html
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
import mistune

register = template.Library()


class HighlightRenderer(mistune.Renderer):
    """
    Source: https://github.com/lepture/mistune/issues/54
    """

    def default(self, code):
        return '\n<pre><code>%s</code></pre>\n' % mistune.escape(code)

    def environment(self, code, name: str):
        return '\n<div class="%s">%s</div>\n' % (name, mistune.markdown(code))

    def block_code(self, code, lang):
        if not lang:
            self.default(code)
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            # A lexer couldn't be found, so its probably a custom environment
            return self.environment(code, lang)
        else:
            formatter = html.HtmlFormatter(lineseparator="<br>")
            return highlight(code, lexer, formatter)


_markdown = mistune.Markdown(renderer=HighlightRenderer())


@register.filter('markdown')
def markdown(value):
    try:
        return _markdown(value)
    except:
        # Default to the non-fancy markdown output
        return mistune.markdown(value)
