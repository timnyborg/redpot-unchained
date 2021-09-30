from django import template

from ..models import TutorModule
from ..utils.expense_forms import template_options

register = template.Library()


@register.inclusion_tag('tags/tutor_module_menu.html', takes_context=True)
def tutor_module_menu(context, tutor_module: TutorModule):
    expense_templates = template_options(tutor_module.module)
    return {
        'request': context['request'],  # for ?next=
        'tutor_module': tutor_module,
        'expense_templates': expense_templates,
        'contracts': tutor_module.contracts.all(),
    }
