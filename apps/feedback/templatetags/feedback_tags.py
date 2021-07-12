from django import template

register = template.Library()


@register.simple_tag
def score_color(score):
    """Color formats the score value"""
    if isinstance(score, int) or isinstance(score, float):
        if score > 3.5:
            return 'feedback-green'
        elif score > 2.5:
            return 'feedback-orange'
        elif score >= 0:
            return 'feedback-red'
    else:
        return 'feedback-gray'
