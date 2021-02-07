from django import template
from ..models import TutorModule

register = template.Library()


@register.inclusion_tag('tags/tutor_module_menu.html')
def tutor_module_menu(tutor_module):
    if tutor_module.module.non_credit_bearing:
        expense_templates = [
            ('weekly', 'Weekly classes'),
            ('nonaccredited', 'Non-accredited'),
            ('undergraduate_award', 'Undergraduate award'),
            ('postgraduate', 'Postgraduate'),
        ]
    else:
        expense_templates = [
            ('weekly', 'Weekly classes'),
            ('day-weekend', 'Day & Weekend courses'),
            ('undergraduate_award', 'Undergraduate award'),
            ('postgraduate', 'Postgraduate'),
        ]

    if not isinstance(tutor_module, TutorModule):
        raise TypeError('tutor_module must be an instance of the TutorModule class')
    return {'tutor_module': tutor_module, 'expense_templates': expense_templates}
