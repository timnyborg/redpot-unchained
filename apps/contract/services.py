from datetime import datetime

from apps.contract import models
from apps.core.utils.postal import FormattedAddress
from apps.tutor.models import RightToWorkType


def generate_fixed_properties(*, contract: models.Contract) -> dict:
    """Produces a set of fixed contract attributes, which won't change if related models are edited
    Could be part of Contract.save()
    """
    tutor = contract.tutor_module.tutor
    student = tutor.student
    module = contract.tutor_module.module
    address = student.get_default_address()
    return {
        'full_name': f"{student.title or ''} {student.firstname} {student.surname}",
        'salutation': f"{student.title or student.firstname} {student.surname}",
        'doc_date': datetime.today(),
        'address': FormattedAddress(address).as_list(),
        'module': {'title': module.title, 'code': module.code},
        'list_a_rtw': tutor.rtw_type == RightToWorkType.PERMANENT,
        'overseas_rtw': tutor.rtw_type == RightToWorkType.OVERSEAS,
    }
