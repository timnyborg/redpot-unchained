from typing import List
from apps.module.models import Module


def template_options(module: Module) -> List[tuple]:
    """Return a the expense form templates available for a given module
       Currently a simple binary, but could involve more complicated logic, or even enabled/disabled flags
    """
    if module.non_credit_bearing:
        return [
            ('weekly', 'Weekly classes'),
            ('nonaccredited', 'Non-accredited'),
            ('undergraduate_award', 'Undergraduate award'),
            ('postgraduate', 'Postgraduate'),
        ]
    else:
        return [
            ('weekly', 'Weekly classes'),
            ('day-weekend', 'Day & Weekend courses'),
            ('undergraduate_award', 'Undergraduate award'),
            ('postgraduate', 'Postgraduate'),
        ]
