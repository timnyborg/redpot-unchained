from django import template
from ..models import TutorFee
register = template.Library()


@register.inclusion_tag('tags/payment_status_tag.html')
def payment_status_icon(payment: TutorFee):
    statuses = {
        'Raised': ('fa-ellipsis-h', 'text-info'),
        'Approved': ('fa-thumbs-up', 'text-warning'),
        'Transferred': ('fa-check', 'text-success'),
        'Failed': ('fa-exclamation-triangle', 'text-danger'),
        'Cancelled': ('fa-remove', 'text-danger'),
    }
    icon_class, text_class = statuses.get('Raised', ('', ''))
    icon_class += ' fas fa-fw'
    return {
        'icon_class': icon_class,
        'text_class': text_class,
        'status': str(payment.status)
    }
