from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from apps.core.utils.celery import mail_on_failure
from redpot.celery import app

from .models import Module


@app.task(name='update_module_statuses')
@mail_on_failure
def update_module_statuses() -> int:
    """Routine to loop through modules set for automatic management update their statuses"""
    modules = (
        Module.objects.filter(
            auto_publish=True,  # Set for automatic
            publish_date__isnull=False,  # Publishing date is required
        )
        # And some simple exclusions:
        .exclude(
            # courses not yet publishable
            is_published=False,
            publish_date__gt=datetime.now(),
        )
        .exclude(
            # courses long since unpublished
            is_published=False,
            unpublish_date__lt=datetime.now(),
        )
        .order_by('id')
    )

    for module in modules:
        result = module.update_status()
        if result['changed'] and module.email and 'conted' in module.email:  # Don't email non-departmental addresses
            # Email the update
            context = {
                'module': module,
                'new_status': module.status.description,
                'canonical_url': settings.CANONICAL_URL,
            }
            body = render_to_string('email/module_status_change.html', context=context)

            message = EmailMessage(
                subject='Module status change: %s' % module.title,
                # Only send to dev while testing
                to=[settings.SUPPORT_EMAIL if settings.DEBUG else module.email],
                bcc=[settings.SUPPORT_EMAIL],
                from_email=settings.SUPPORT_EMAIL,
                body=body,
            )
            message.content_subtype = 'html'
            message.send(fail_silently=True)

    return len(modules)
