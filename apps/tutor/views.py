from django.http import HttpResponse, Http404
import re
import os
import pathlib
from .utils.mail_merge import mail_merge, MailMergeView
from .models import TutorModule

"""
For example, the below CBV, but as a FBV

def expense_form(request, pk, mode, template):
    if mode == 'module':
        queryset = TutorModule.objects.filter(module=pk)
    elif mode == 'record':
        queryset = TutorModule.objects.filter(pk=pk)
    elif mode == 'modules':
        # Wildcard based matching
        queryset = TutorModule.objects.filter(module__code__like=kwargs['search'])
    else:
        raise Exception('Invalid arguments')

    # Join in required tables
    # Todo: remove test limiting the results while docx-mailmerge is still buggy
    records = queryset.select_related('module', 'tutor__student').all()[:2]
    record = records[0]

    if mode == 'module':
        filename = '%s_expense_forms.docx' % record.module.code
    elif mode == 'record':
        filename = f'{record.tutor.student.firstname}_{record.tutor.student.surname}' \
                    '_{record.module.code}_expense_form.docx'.replace(' ', '_')
    else:
        filename = 'batch_expense_form.docx'

    template = f'tutor_expense_forms/{template}.docx'
    path = os.path.join(pathlib.Path(__file__).parent.absolute(), 'utils/templates', template)

    try:
        with open(path, 'rb') as file:
            doc = mail_merge(
                docx_file=file,
                filename=filename,
                records=[dict(
                    tutor_name="('%(title)s %(firstname)s %(surname)s' % record.tutor.student).strip()",
                    nickname=record.tutor.student.nickname,
                    birthdate=record.tutor.student.birthdate.strftime('%d %B %y') if record.tutor.student.birthdate else '',
                    gender=record.tutor.student.gender,

                    line1='record.address.line1',
                    line2='record.address.line2',
                    line3='record.address.line3',
                    town='record.address.town',
                    county_state='record.address.countystate',
                    country='record.address.country',
                    postcode='record.address.postcode',

                    bankname=record.tutor.bankname,
                    branchaddress=record.tutor.branchaddress,
                    sortcode=record.tutor.sortcode,
                    accountno=record.tutor.accountno,
                    accountname=record.tutor.accountname,
                    iban=record.tutor.iban,
                    swift=record.tutor.swift,

                    nino=record.tutor.nino or "record.nationality.name",
                    appointment_id=record.tutor.appointment_id,
                    employee_no=record.tutor.employee_no,

                    title=record.module.title,
                    code=record.module.code,
                    start_date=record.module.start_date.strftime('%d %B %y') if record.module.start_date else '',
                    end_date=record.module.end_date.strftime('%d %B %y') if record.module.end_date else '',
                    accredited=u'□' if record.module.non_credit_bearing else u'X',
                    cost_centre=record.module.cost_centre,
                    activity=record.module.activity_code,
                    source_of_funds=record.module.source_of_funds,
                ) for record in records]
            )
    except FileNotFoundError:
        raise Http404

    response = HttpResponse(doc, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-disposition'] = 'attachment; filename=%s' % re.sub('[,()\']', '', str(filename))
    return response
"""


class ExpenseFormView(MailMergeView):
    def get_filename(self, queryset):
        record = queryset[0]
        if self.kwargs['mode'] == 'module':
            return '%s_expense_forms.docx' % record.module.code
        elif self.kwargs['mode'] == 'single':
            return f'{record.tutor.student.firstname}_{record.tutor.student.surname}' \
                       f'_{record.module.code}_expense_form.docx'.replace(' ', '_')
        else:
            return 'batch_expense_form.docx'

    def get_template_file(self, queryset):
        return os.path.join(
            pathlib.Path(__file__).parent.absolute(),
            'utils/templates',
            self.kwargs['template'] + '.docx'
        )

    def get_queryset(self):
        queryset = TutorModule.objects
        if self.kwargs['mode'] == 'module':
            return queryset.filter(module=self.kwargs['pk'])
        elif self.kwargs['mode'] == 'single':
            return queryset.filter(pk=self.kwargs['pk'])
        elif self.kwargs['mode'] == 'search':
            # Wildcard based matching
            return queryset.filter(module__code__like=self.kwargs['search'])

    def get_context_data(self, *, object_list=None, **kwargs):
        return [
            dict(
                tutor_name="('%(title)s %(firstname)s %(surname)s' % record.tutor.student).strip()",
                nickname=record.tutor.student.nickname,
                birthdate=record.tutor.student.birthdate.strftime('%d %B %y') if record.tutor.student.birthdate else '',
                gender=record.tutor.student.gender,

                line1='record.address.line1',
                line2='record.address.line2',
                line3='record.address.line3',
                town='record.address.town',
                county_state='record.address.countystate',
                country='record.address.country',
                postcode='record.address.postcode',

                bankname=record.tutor.bankname,
                branchaddress=record.tutor.branchaddress,
                sortcode=record.tutor.sortcode,
                accountno=record.tutor.accountno,
                accountname=record.tutor.accountname,
                iban=record.tutor.iban,
                swift=record.tutor.swift,

                nino=record.tutor.nino or "record.nationality.name",
                appointment_id=record.tutor.appointment_id,
                employee_no=record.tutor.employee_no,

                title=record.module.title,
                code=record.module.code,
                start_date=record.module.start_date.strftime('%d %B %y') if record.module.start_date else '',
                end_date=record.module.end_date.strftime('%d %B %y') if record.module.end_date else '',
                accredited='□' if record.module.non_credit_bearing else 'X',
                cost_centre=record.module.cost_centre,
                activity=record.module.activity_code,
                source_of_funds=record.module.source_of_funds,
            ) for record in self.queryset.all()[:2]
        ]
