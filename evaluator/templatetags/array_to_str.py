from django import template

register = template.Library()

@register.filter
def str_array(arg):
    return [str(el) for el in arg]