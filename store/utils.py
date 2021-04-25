import logging

from django.core.mail import send_mail

log = logging.getLogger(__name__)


def send_confirmation(email, data):
    from .models import Settings

    sets = Settings.objects.filter(
        name__in=[Settings.EMAIL_SUBJECT, Settings.EMAIL_BODY, Settings.EMAIL_FROM]).values()
    sets = {s['name']: s['value'] for s in sets}

    subject = sets[Settings.EMAIL_SUBJECT] % data
    body = sets[Settings.EMAIL_BODY] % data
    from_ = sets[Settings.EMAIL_FROM]

    sent_num = send_mail(subject,
                         body,
                         from_,
                         [email])
    if sent_num != 1:
        log.error('Unable to send e-mail to %s.', email)
