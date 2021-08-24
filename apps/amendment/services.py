import re

from apps.finance.models import Ledger, TransactionTypes
from apps.invoice.models import Invoice
from apps.module.models import Module

from . import models


def get_narrative(*, amendment: models.Amendment) -> str:
    """Populate default value for narrative field"""

    # Todo: this method is a piece of work, and needs rethinking.  Replace with strategy pattern?
    if amendment.type_id == models.AmendmentTypes.TRANSFER:  # Transfer
        if amendment.transfer_module:  # to another course
            if amendment.transfer_module == 'multiple':
                transfer_module = 'multiple'
            else:
                module = Module.objects.filter(pk=amendment.transfer_module).first()
                transfer_module = module.code
            code = amendment.enrolment.module.code
            narrative = f'INF {amendment.id} - Transfer from {code} to {transfer_module}'

        elif amendment.transfer_enrolment:  # to another student
            from_student = amendment.enrolment.qa.student
            to_student = amendment.transfer_enrolment.qa.student
            to_module = amendment.transfer_enrolment.module
            narrative = f'INF {amendment.id} - Transfer from {from_student} to {to_student} on {to_module.code}'
        elif amendment.transfer_invoice:  # to another invoice
            # todo: fix this horrible bit of double-table foreign-keying!  Should only point to invoice
            invoice = Invoice.objects.filter(pk=amendment.source_invoice).first()
            if invoice:
                source = f'invoice {invoice}'
            else:
                ledger = Ledger.objects.filter(pk=amendment.source_invoice).first()
                source = f'payment {ledger.narrative}'
            narrative = f'INF {amendment.id} - Transfer from {source} to {amendment.transfer_invoice}'
        else:
            raise Exception('Amendment lacks an enrolment, student, or invoice to transfer to')

    elif amendment.type_id == models.AmendmentTypes.AMENDMENT:
        narrative = f'INF {amendment.id} - Write off - {amendment.reason}'

    elif amendment.type_id == models.AmendmentTypes.ONLINE_REFUND:
        narrative = f'REF {amendment.id} - Refund - {amendment.reason}'
        ledger_narratives = (
            amendment.enrolment.ledger_set.debts()
            .filter(amount__lt=0, type=TransactionTypes.ONLINE, narrative__like='%contCPG%')
            .values_list('narrative', flat=True)
        )
        if len(ledger_narratives) == 1:  # Only if there's only one
            online_payment = re.findall(r'contCPG\d*', ledger_narratives[0])[0]
            narrative += f' - {online_payment}'
    elif amendment.type_id == models.AmendmentTypes.CREDIT_CARD_REFUND:
        narrative = f'REF {amendment.id} - Refund (cc) - {amendment.reason}'
    elif amendment.type_id == models.AmendmentTypes.RCP_REFUND:
        narrative = f'REF {amendment.id} - Refund (rcp) - {amendment.reason}'
        ledger = amendment.enrolment.ledger_set.debts().filter(amount__lt=0, type=TransactionTypes.RCP).first()
        if ledger:
            narrative += f" - …{ledger.narrative[-80:-10]}"
    elif amendment.type_id == models.AmendmentTypes.OTHER_REFUND:
        narrative = f'REF {amendment.id} - Refund (paper form)'
    elif amendment.type_id == models.AmendmentTypes.BANK_REFUND:
        narrative = f'REF {amendment.id} - Refund (bank return) - {amendment.reason}'
    else:
        raise Exception(f'Invalid amendment type: {amendment.type}')

    return narrative
