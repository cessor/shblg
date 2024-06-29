from django import template
from pygments import highlight
from pygments.formatters import html
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
import mistune

register = template.Library()


class HighlightRenderer(mistune.HTMLRenderer):
    """
    Source: https://github.com/lepture/mistune/issues/54
    """
    def default(self, code):
        return f"\n<pre><code>{mistune.escape(code)}</code></pre>\n"

    def environment(self, code, name: str):
        return f'\n<div class="{name}">{mistune.markdown(code)}</div>\n'

    def block_code(self, code, info=None):
        if not info:
            return self.default(code)

        try:
            lexer = get_lexer_by_name(info, stripall=True)
        except ClassNotFound:
            # A lexer couldn't be found, so its probably a custom environment,
            # e.g. "note, caution, tldr"
            return self.environment(code, info)

        formatter = html.HtmlFormatter(lineseparator="<br>")
        return highlight(code, lexer, formatter)


_markdown = mistune.Markdown(renderer=HighlightRenderer())


@register.filter('markdown')
def markdown(value):
    try:
        return _markdown(value)
    except: #pylint: disable=bare-except
        # Default to the non-fancy markdown output
        return mistune.markdown(value)
