import datetime
import statistics

import xlwt

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.feedback.models import Feedback
from apps.module.models import Module


def process_and_send_emails(module: Module) -> None:
    enrolments = (
        module.enrolments.filter(
            status__in=[10, 71, 90],
            qa__student__email__email__isnull=False,
            qa__student__email__is_default=True,
        )
        .select_related('module', 'qa', 'qa__student', 'qa__student__email')
        .values(
            'qa__student__id',
            'qa__student__firstname',
            'qa__student__surname',
            'id',
            'qa__student__email__email',
            'module',
            'module__id',
            'module__title',
            'module__code',
            'module__email',
            'module__portfolio__email',
        )
        .order_by(
            '-qa__student__email__email',
            'qa__student__surname',
            'qa__student__firstname',
        )
    )

    for enrolment in enrolments:
        email_context = {
            'firstname': enrolment['qa__student__firstname'],
            'email': enrolment['qa__student__email__email'],
            'module': enrolment['module'],
            'module_id': enrolment['module__id'],
            'module_title': enrolment['module__title'],
            'enrolment': enrolment['id'],
        }
        mod_contact = (
            enrolment['module__email'] if enrolment['module__email'] else enrolment['module__portfolio__email']
        )

        # Create object in table if object didn't exist
        student_feedback, created = Feedback.objects.get_or_create(enrolment=email_context['enrolment'], module=module)

        subject = f"Your feedback on {email_context['module_title']}"
        to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [email_context['email']]
        if created:
            html_message = render_to_string('feedback/email/feedback_email.html', email_context)
            # todo: determine if it's worthwhile to bcc webmaster
            send_mail(subject, strip_tags(html_message), mod_contact, to, html_message=html_message)

            student_feedback.notified = datetime.datetime.now()
            student_feedback.save()

        elif not student_feedback.reminder:
            html_message = render_to_string('feedback/email/feedback_email_reminder.html', email_context)
            send_mail(subject, strip_tags(html_message), mod_contact, to, html_message=html_message)

            student_feedback.reminder = datetime.datetime.now()
            student_feedback.save()


def get_mean_value(list_of_ints):  # Takes a list of integers and returns a mean value
    value = round(statistics.mean(list_of_ints or [0]), 1)
    return value


def get_module_info(module_id):
    module = Module.objects.filter(id=module_id).values('id', 'title', 'code', 'start_date', 'end_date', 'email')
    module_info = module.first()
    return module_info


def get_module_summary(module_id):
    module_summary = {}
    module = Module.objects.filter(id=module_id).values('id', 'title')
    module_info = module.first()

    module_summary['id'] = module_info['id']
    module_summary['title'] = module_info['title']

    module_feedback_sent = Feedback.objects.filter(module=module_id)
    module_feedback_submitted = Feedback.objects.filter(module=module_id, submitted__isnull=False)

    module_summary['teaching'] = get_mean_value(
        module_feedback_submitted.values_list('rate_tutor', flat=True).filter(rate_tutor__gt=0)
    )
    module_summary['content'] = get_mean_value(
        module_feedback_submitted.values_list('rate_content', flat=True).filter(rate_content__gt=0)
    )
    module_summary['facility'] = get_mean_value(
        module_feedback_submitted.values_list('rate_facilities', flat=True).filter(rate_facilities__gt=0)
    )
    module_summary['admin'] = get_mean_value(
        module_feedback_submitted.values_list('rate_admin', flat=True).filter(rate_admin__gt=0)
    )
    module_summary['catering'] = get_mean_value(
        module_feedback_submitted.values_list('rate_refreshments', flat=True).filter(rate_refreshments__gt=0)
    )
    module_summary['accommodation'] = get_mean_value(
        module_feedback_submitted.values_list('rate_accommodation', flat=True).filter(rate_accommodation__gt=0)
    )
    module_summary['sent'] = module_feedback_sent.count()
    module_summary['returned'] = module_feedback_submitted.count()
    module_summary['average'] = get_mean_value(
        [
            module_summary['teaching'],
            module_summary['content'],
            module_summary['facility'],
            module_summary['admin'],
            module_summary['catering'],
            module_summary['accommodation'],
        ]
    )
    high_scores = module_feedback_submitted.filter(avg_score__gt=3.5).count()
    total_scores = module_feedback_submitted.filter(avg_score__isnull=False).count()
    try:
        module_summary['satisfied'] = int(float(high_scores) / float(total_scores) * 100)
    except ZeroDivisionError:
        module_summary['satisfied'] = None
    return module_summary


def get_module_feedback_details(module_id):
    feedback_results = Feedback.objects.filter(module=module_id, submitted__isnull=False).order_by('submitted')
    feedback_details_dict = {}

    for feedback_result in feedback_results:
        feedback_detail = {}
        feedback_detail['id'] = feedback_result.id
        feedback_detail['name'] = feedback_result.your_name if feedback_result.your_name else 'Anonymous'
        feedback_detail['submitted_on'] = feedback_result.submitted.strftime('%H:%M on %d-%b-%Y')
        feedback_detail['average'] = round(float(feedback_result.avg_score or 0), 1)
        feedback_detail['teaching'] = feedback_result.rate_tutor
        feedback_detail['content'] = feedback_result.rate_content
        feedback_detail['facility'] = feedback_result.rate_facilities
        feedback_detail['admin'] = feedback_result.rate_admin
        feedback_detail['catering'] = feedback_result.rate_refreshments
        feedback_detail['accommodation'] = feedback_result.rate_accommodation
        feedback_detail['comment'] = feedback_result.comments

        feedback_details_dict[feedback_detail['id']] = feedback_detail
    return feedback_details_dict


def export_users_xls(module_id):
    module_info = get_module_info(module_id)

    response = HttpResponse(content_type='application/ms-excel')
    file_name = f"feedback_{module_info['code']}_{datetime.datetime.now().strftime('%Y-%m-%d')}.xls"
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Feedback')

    # Sheet title in first row
    row_num = 0
    sheet_title = f'''Feedback for {module_info['title']}({module_info['code']}) -
    ({module_info['start_date'].strftime('%d-%b-%Y')} to {module_info['end_date'].strftime('%d-%b-%Y')})'''

    font_style = xlwt.XFStyle()
    font_style.font.bold = True  # applies bold format
    ws.write(row_num, 0, sheet_title, font_style)  # Write sheet title

    # Create a table for module_summary
    row_num = 2
    column_headers1 = [
        'Satisfied (%)',
        'Average',
        'Teaching',
        'Content',
        'Facility',
        'Admin',
        'Catering',
        'Accomm',
        'Sent',
        'Returned',
    ]

    for col_num in range(len(column_headers1)):
        ws.write(row_num, col_num, column_headers1[col_num], font_style)

    module_summary = get_module_summary(module_id)
    column_data1 = [
        module_summary['satisfied'],
        module_summary['average'],
        module_summary['teaching'],
        module_summary['content'],
        module_summary['facility'],
        module_summary['admin'],
        module_summary['catering'],
        module_summary['accommodation'],
        module_summary['sent'],
        module_summary['returned'],
    ]
    row_num = 3
    font_style = xlwt.XFStyle()
    for col_num in range(len(column_data1)):
        ws.write(row_num, col_num, column_data1[col_num], font_style)

    # Create a table for feedback_details
    row_num = 5
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    column_headers2 = ['Name', 'Average', 'Teaching', 'Content', 'Facility', 'Admin', 'Catering', 'Accomm', 'Comments']

    for col_num in range(len(column_headers2)):
        ws.write(row_num, col_num, column_headers2[col_num], font_style)

    module_feedback_details = get_module_feedback_details(module_id)
    font_style = xlwt.XFStyle()
    for feedback_detail in module_feedback_details.values():
        row_num += 1
        column_data2 = [
            feedback_detail['name'],
            feedback_detail['average'],
            feedback_detail['teaching'],
            feedback_detail['content'],
            feedback_detail['facility'],
            feedback_detail['admin'],
            feedback_detail['catering'],
            feedback_detail['accommodation'],
            feedback_detail['comment'],
        ]
        for col_num in range(len(column_data2)):
            ws.write(row_num, col_num, column_data2[col_num], font_style)

    wb.save(response)
    return response
