from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def phone_format(num):
    try:
        # strip all non-numeric chars
        result = []
        for char in num:
            if char.isdigit():
                result.append(char)
        # if 10 digits (###) ###-####
        if len(result) == 10:
            result.insert(-4, '-')
            result.insert(3, ' ')
            result.insert(3, ')')
            result.insert(0, '(')
        return ''.join(result)
    except:
        return num
