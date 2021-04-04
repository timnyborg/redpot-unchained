from typing import Dict

from apps.module.models import Module


def template_options(module: Module) -> Dict:
    """Return a the expense form templates available for a given module
    Currently a simple binary, but could involve more complicated logic, or even enabled/disabled flags
    """
    if module.non_credit_bearing:
        return {
            'weekly': 'Weekly classes',
            'nonaccredited': 'Non-accredited',
            'undergraduate_award': 'Undergraduate award',
            'postgraduate': 'Postgraduate',
        }
    else:
        return {
            'weekly': 'Weekly classes',
            # todo: find out why D&W is here.  AG added in a commit in Sept 2019
            'day-weekend': 'Day & Weekend courses',
            'undergraduate_award': 'Undergraduate award',
            'postgraduate': 'Postgraduate',
        }
