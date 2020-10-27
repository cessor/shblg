from django import template
import mistune

register = template.Library()


@register.filter('markdown')
def markdown(value):
    return mistune.markdown(value)
