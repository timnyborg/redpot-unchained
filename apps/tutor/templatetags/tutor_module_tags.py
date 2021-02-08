from django import template
from ..models import TutorModule
from ..utils.expense_forms import template_options
register = template.Library()


@register.inclusion_tag('tags/tutor_module_menu.html')
def tutor_module_menu(tutor_module: TutorModule):
    expense_templates = template_options(tutor_module.module)
    return {'tutor_module': tutor_module, 'expense_templates': expense_templates}
