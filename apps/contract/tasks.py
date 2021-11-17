from redpot.celery import app

from . import services


@app.task(name='mail_pending_contracts_signature')
def mail_pending_contracts_signature():
    return services.mail_pending_contracts_signature()


@app.task(name='mail_pending_contracts_approval')
def mail_pending_contracts_approval():
    return services.mail_pending_contracts_approval()
