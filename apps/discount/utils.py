from datetime import datetime
from django.db.models import Value, Min, CharField, Q, QuerySet
from django.db.models.functions import Replace
from apps.module.models import Module
from .models import Discount


def get_module_discounts(module: Module) -> QuerySet:
    """ Retrieves a list of applicable discounts for a given module, annotated with availability"""
    return Discount.objects.annotate(
        search_module_code=Value(module.code, output_field=CharField()),
        # 0 indicates all students
        eligibility=Min('student__student')
    ).filter(
        # Get unexpired discounts, limited to this portfolio if required
        Q(expires_on=None) | Q(expires_on__gt=datetime.now()),
        Q(portfolio=module.portfolio_id) | Q(portfolio=None),
        # We currently allow use of * in place of %
        search_module_code__like=Replace('module_mask', Value('*'), Value('%'))
    )
