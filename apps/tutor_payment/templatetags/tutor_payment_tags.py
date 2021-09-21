from django import template

from ..models import TutorPayment

register = template.Library()


@register.inclusion_tag('tags/payment_status_tag.html')
def payment_status_icon(payment: TutorPayment):
    statuses = {
        'Raised': ('fa-ellipsis-h', 'text-dark'),
        'Approved': ('fa-thumbs-up', 'text-primary'),
        'Transferred': ('fa-check', 'text-success'),
        'Failed': ('fa-exclamation-triangle', 'text-danger'),
        'Cancelled': ('fa-remove', 'text-danger'),
    }
    icon_class, text_class = statuses.get(str(payment.status), ('', ''))
    icon_class += ' fas fa-fw'
    return {
        'icon_class': icon_class,
        'text_class': text_class,
        'status': str(payment.status),
    }
