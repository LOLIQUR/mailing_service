from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Mailing, MailingAttempt


def send_mailing(mailing: Mailing, user) -> dict:
    now = timezone.now()

    # Проверка прав
    if user.role != 'manager' and mailing.owner != user:
        return {'success': False, 'error': 'У вас нет прав на эту рассылку.'}

    if not (mailing.start_time <= now <= mailing.end_time):
        return {'success': False, 'error': 'Время рассылки не наступило или уже прошло.'}

    recipients = mailing.recipients.all()
    if not recipients:
        return {'success': False, 'error': 'У рассылки нет получателей.'}

    successful = 0
    failed = 0
    attempts = []

    for client in recipients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False,
            )
            attempts.append(MailingAttempt(
                mailing=mailing,
                status=MailingAttempt.STATUS_SUCCESS,
                server_response='OK'
            ))
            successful += 1
        except Exception as e:
            attempts.append(MailingAttempt(
                mailing=mailing,
                status=MailingAttempt.STATUS_FAILED,
                server_response=str(e)
            ))
            failed += 1

    MailingAttempt.objects.bulk_create(attempts)

    return {
        'success': True,
        'successful': successful,
        'failed': failed,
        'total': successful + failed,
    }
