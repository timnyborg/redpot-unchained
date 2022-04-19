import datetime
import statistics
from pathlib import Path

import xlwt
from weasyprint import CSS, HTML

from django.conf import settings
from django.core import mail
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.text import slugify

from apps.enrolment.models import CONFIRMED_STATUSES
from apps.feedback.models import Feedback, FeedbackAdmin
from apps.module.models import Module
from apps.student.models import Student
from apps.tutor.models import TutorModule


def process_and_send_emails(module: Module) -> None:
    # Avoid sending email to external people (WEA for example, by falling back to portfolio)
    admin_email = module.email if '@conted' in module.email else module.portfolio.email
    mail_sent = False
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

        # Create object in table if object didn't exist
        student_feedback, created = Feedback.objects.get_or_create(enrolment=email_context['enrolment'], module=module)

        subject = f"Your feedback on {email_context['module_title']}"
        to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [email_context['email']]
        if created:
            html_message = render_to_string('feedback/email/feedback_email.html', email_context)
            send_mail(subject, strip_tags(html_message), admin_email, to, html_message=html_message)

            student_feedback.notified = datetime.datetime.now()
            student_feedback.save()
            mail_sent = True

        elif not student_feedback.reminder:
            html_message = render_to_string('feedback/email/feedback_email_reminder.html', email_context)
            send_mail(subject, strip_tags(html_message), admin_email, to, html_message=html_message)

            student_feedback.reminder = datetime.datetime.now()
            student_feedback.save()
            mail_sent = True

    if mail_sent:
        subject = f"Automated feedback requests for {email_context['module_title']}"
        to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [admin_email]
        cc = [settings.SUPPORT_EMAIL] if settings.DEBUG else ['webmaster@conted.ox.ac.uk']
        html_message = (
            f"Requests have been sent out for {email_context['module_title']}.\n\nYou "
            f"will be emailed when the results are in."
        )
        send_mail(subject, html_message, admin_email, to, cc, html_message=html_message)


def mail_dos(module: Module):
    live_email = module.email if '@conted' in module.email else module.portfolio.email
    sender = [settings.SUPPORT_EMAIL] if settings.DEBUG else live_email
    recipient = TutorModule.objects.filter(
        module=module.id, director_of_studies=True, tutor__student__email__is_default=True
    ).first()

    attended = module.enrolments.filter(status__in=CONFIRMED_STATUSES).count()

    sent = False

    if recipient:
        email_context = {
            'email': live_email,
            'module_code': module.code,
            'portfolio': module.portfolio,
            'dos': recipient['tutor__student__firstname'],
            'attended': attended,
            'module_start_month': module.start_date.month,
            'module_start_date': module.start_date,
        }
        subject = f"Student feedback - {module.title}"
        html_message = render_to_string('feedback/email/notifydos.html', email_context)
        to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [recipient['tutor__student__email__email']]
        cc = [settings.SUPPORT_EMAIL] if settings.DEBUG else ['webmaster@conted.ox.ac.uk']
        sent = send_mail(subject, strip_tags(html_message), sender, to, cc, html_message=html_message)
    return sent


def mail_course_admin(module, dos_emailed=None):
    email_context = {'title': module.title, 'module_code': module.code, 'dos_emailed': dos_emailed}

    sender = 'webmaster@conted.ox.ac.uk'
    live_email = module.email if '@conted' in module.email else module.portfolio.email
    to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [live_email]
    cc = [settings.SUPPORT_EMAIL] if settings.DEBUG else [sender]
    subject = f"ACTION: feedback results {module.title} - {module.code}"
    html_message = render_to_string('feedback/email/notifyadmin.html', email_context)

    if to:
        send_mail(subject, strip_tags(html_message), sender, to, cc, html_message=html_message)
    else:
        to = ['redpot-support@conted.ox.ac.uk']
        subject = f"No course admin for {module.title} - {module.code}"
        html_message = 'Course feedback results are ready, but no course admin!'
        send_mail(subject, html_message, sender, to, cc, html_message=html_message)


def email_admin_report(module: Module, tutor_ids: list) -> None:
    """Send feedback report to course admin"""
    from_email = module.email
    tutors_ids = [int(tutor) for tutor in tutor_ids]
    tutors = Student.objects.filter(pk__in=tutors_ids).order_by('surname')
    tutors = [f'{tutor.title} {tutor.firstname} {tutor.surname}' for tutor in tutors]  # Get only tutor names
    url = settings.CANONICAL_URL
    context = {'url': url, 'from': from_email, 'title': module.title, 'code': module.code, 'tutors': tutors}

    body = render_to_string('feedback/email/updateadmin.html', context)

    to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [module.email]
    bcc = [settings.SUPPORT_EMAIL] if settings.DEBUG else ['webmaster@conted.ox.ac.uk']
    subject = 'Feedback [' + module.title + ']'
    pdf_file_name = f"Feedback-report-{module.code}-{slugify(module.title)}.pdf"
    pdf_context = {
        'module': module,
        'module_summary': get_module_summary(module.id),
        'tutors': get_module_tutors(module.id),
        'feedback_data_dict': get_module_feedback_details(module.id),
        'comments_list': get_module_comments(module.id),
        'context_data': 'This is a context data',
        'module_summary_headers': [
            'Module Title',
            'Satisfied(%)',
            'Average',
            'Teaching',
            'Content',
            'Facilities',
            'Admin',
            'Catering',
            'Accomm',
            'Sent',
            'Returned',
        ],
    }

    email = mail.EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to,
        bcc=bcc,
    )
    email.content_subtype = 'html'
    content = make_pdf(
        html_path='feedback/pdfs/module_feedback.html',
        css_path=f"{Path(__file__).parent}/static/css/pdf.css",
        pdf_context=pdf_context,
    )
    email.attach(filename=pdf_file_name, content=content, mimetype='application/pdf')
    email.send()


def email_tutor_report(module: Module, tutor_ids: list) -> None:
    """Send feedback report to selected course Tutors"""
    module_id = module.id
    url = settings.CANONICAL_URL
    from_email = module.email

    bcc = [settings.SUPPORT_EMAIL] if settings.DEBUG else ['webmaster@conted.ox.ac.uk']
    subject = f"Student feedback for { module.title }"
    tutors_stud_ids = [int(tutor) for tutor in tutor_ids]
    tutors = (
        Student.objects.filter(pk__in=tutors_stud_ids, email__is_default=1)
        .order_by('surname')
        .prefetch_related('emails')
    )
    pdf_file_name = f"Feedback-report-{module.code}-{slugify(module.title)}.pdf"

    for tutor in tutors:
        tutor_firstname = tutor.firstname
        tutor_email = tutor.emails.get(is_default=True).email or ''

        if tutor_email:
            to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [tutor_email]
            context = {
                'url': url,
                'from': from_email,
                'title': module.title,
                'code': module.code,
                'tutor_firstname': tutor_firstname,
                'portfolio': module.portfolio,
                'email': module.email,
            }

            body = render_to_string('feedback/email/updatetutor.html', context)

            email = mail.EmailMessage(
                subject=subject,
                body=body,
                from_email=from_email,
                to=to,
                bcc=bcc,
            )
            email.content_subtype = 'html'
            pdf_context = {
                'module': module,
                'module_summary': get_module_summary(module_id),
                'tutors': get_module_tutors(module_id),
                'feedback_data_dict': get_module_feedback_details(module_id),
                'comments_list': get_module_comments(module_id),
                'context_data': 'This is a context data',
                'module_summary_headers': [
                    'Module Title',
                    'Satisfied(%)',
                    'Average',
                    'Teaching',
                    'Content',
                    'Facilities',
                    'Admin',
                    'Catering',
                    'Accomm',
                    'Sent',
                    'Returned',
                ],
            }
            content = make_pdf(
                html_path='feedback/pdfs/module_feedback.html',
                css_path=f"{Path(__file__).parent}/static/css/pdf.css",
                pdf_context=pdf_context,
            )
            email.attach(filename=pdf_file_name, content=content, mimetype='application/pdf')
            email.send()


def make_pdf(html_path, css_path, pdf_context):
    html_doc = render_to_string(html_path, context=pdf_context)
    content = HTML(string=html_doc).write_pdf(stylesheets=[CSS(css_path)])
    return content


def get_mean_value(list_of_ints):  # Takes a list of integers and returns a mean value
    value = round(statistics.mean(list_of_ints or [0]), 1)
    return value


def get_module_info(module_id):
    module = Module.objects.filter(id=module_id).values(
        'id', 'title', 'code', 'start_date', 'end_date', 'email', 'portfolio'
    )
    module_info = module.first()
    return module_info


def get_module_summary(module_id):
    module_summary = {}
    module = Module.objects.filter(id=module_id).values('id', 'title')
    module_info = module.first()

    module_summary['id'] = module_info['id']
    module_summary['title'] = module_info['title']

    module_feedback_sent = Feedback.objects.filter(module=module_id).count()
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
    module_summary['sent'] = module_feedback_sent
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


def get_module_tutors(module_id):
    tutors_set = TutorModule.objects.filter(module=module_id, is_teaching=True).order_by('tutor__student__surname')
    tutors = [
        f'{tutor.tutor.student.nickname} {tutor.tutor.student.surname}'
        if tutor.tutor.student.nickname
        else f'{tutor.tutor.student.firstname} {tutor.tutor.student.surname}'
        for tutor in tutors_set
    ]

    return tutors


def get_module_comments(module_id):
    comments_list = []
    admin_comments_set = FeedbackAdmin.objects.filter(module=module_id).order_by('updated')
    for comment_row in admin_comments_set:
        values = {}
        values['comment'] = comment_row.admin_comments
        values['uploaded_by'] = comment_row.person
        values['uploaded_on'] = (
            comment_row.updated.strftime('%H:%M on %d-%b-%Y')
            if isinstance(comment_row.updated, datetime.date)
            else '-'
        )
        comments_list.append(values)

    return comments_list


def export_users_xls(module: Module) -> HttpResponse:
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Feedback')

    # Sheet title in first row
    row_num = 0
    sheet_title = f"Feedback for {module.title} ({module.code})"

    font_style = xlwt.XFStyle()
    font_style.font.bold = True  # applies bold format
    ws.write(row_num, 0, sheet_title, font_style)  # Write sheet title

    # Create a table for module_summary
    row_num = 2
    headers = [
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

    for column, data in enumerate(headers):
        ws.write(row_num, column, data, font_style)

    module_summary = get_module_summary(module.id)
    row = [
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
    for column, data in enumerate(row):
        ws.write(row_num, column, data, font_style)

    # Create a table for feedback_details
    row_num = 5
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    headers = ['Name', 'Average', 'Teaching', 'Content', 'Facility', 'Admin', 'Catering', 'Accomm', 'Comments']

    for column, data in enumerate(headers):
        ws.write(row_num, column, data, font_style)

    feedback = module.feedback_set.filter(submitted__isnull=False)
    font_style = xlwt.XFStyle()
    for item in feedback:
        row_num += 1
        row = [
            item.your_name or 'Anonymous',
            round(item.avg_score, 1),
            item.rate_tutor,
            item.rate_content,
            item.rate_facilities,
            item.rate_admin,
            item.rate_refreshments,
            item.rate_accommodation,
            item.comments,
        ]
        for column, data in enumerate(row):
            ws.write(row_num, column, data, font_style)

    file_name = f"feedback_{module.code}_{datetime.datetime.now():%Y-%m-%d}.xls"
    response = HttpResponse(
        content_type='application/ms-excel', headers={'Content-Disposition': f'attachment; filename={file_name}'}
    )
    wb.save(response)
    return response
