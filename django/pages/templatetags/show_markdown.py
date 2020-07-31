from django import template
import markdown

register = template.Library()

@register.filter
def show_markdown(text):
    return markdown.markdown(text)


@register.filter
def timeformat(datetime):
    return datetime.strftime("%d.%m.%Y %H:%M")

@register.filter
def dateformat(datetime):
    return datetime.strftime("%d.%m.%Y")