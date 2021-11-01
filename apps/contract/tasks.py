from redpot.celery import app

from . import services


@app.task(name='mail_pending_contracts_signature')
def mail_pending_contracts_signature():
    return services.mail_pending_contracts_signature()
