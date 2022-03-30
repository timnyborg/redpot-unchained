from numbers import Number

from django import template

register = template.Library()


@register.simple_tag
def score_color(score) -> str:
    """Color formats for the score values"""
    if isinstance(score, Number):
        if score > 3.5:
            return 'feedback-green'
        elif score > 2.5:
            return 'feedback-orange'
        elif score >= 0:
            return 'feedback-red'
    else:
        return 'feedback-gray'


@register.simple_tag
def status_color(status):
    """Color formats for the status values"""
    if status == 'Send feedback request':
        return 'feedback-green'
    elif status == 'Send reminder':
        return 'feedback-orange'
    elif status == 'See results':
        return 'feedback-green'
