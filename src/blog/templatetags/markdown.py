from django import template
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
import mistune

register = template.Library()


class HighlightRenderer(mistune.Renderer):
    """
    Source: https://github.com/lepture/mistune/issues/54
    """
    def block_code(self, code, lang):
        print(code)
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter(lineseparator="<br>")
        return highlight(code, lexer, formatter)


_markdown = mistune.Markdown(renderer=HighlightRenderer())


@register.filter('markdown')
def markdown(value):
    return _markdown(value)
