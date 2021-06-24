import socket
from functools import wraps
from typing import Callable, TypeVar

from django.conf import settings
from django.core.mail import send_mail

ReturnType = TypeVar('ReturnType')


def mail_on_failure(func: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
    """A decorator which emails us on task failure

    Usage:

    @app.task
    @mail_on_failure
    def job_name():
        ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> ReturnType:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            server = socket.gethostname()
            send_mail(
                subject=f'Redpot unchained - scheduled task error ({server})',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SUPPORT_EMAIL],
                message=f"""There has been an error with celery job '{func.__name__}' on {server}: {e}""",
            )
            raise

    return wrapper
