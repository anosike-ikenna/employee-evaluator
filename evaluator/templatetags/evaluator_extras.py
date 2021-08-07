from django import template

register = template.Library()

@register.filter
def intstr(arg):
    return str(arg)

@register.filter
def str_array(arg):
    return [str(el) for el in arg]