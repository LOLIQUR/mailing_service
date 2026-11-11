from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from clients.models import Client
from .models import Mailing, MailingAttempt
from .services import send_mailing
from django.core.cache import cache

@login_required
def start_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    result = send_mailing(mailing, request.user)

    if result['success']:
        messages.success(
            request,
            f"Рассылка #{pk} отправлена! Успешно: {result['successful']}, Ошибок: {result['failed']}"
        )
    else:
        messages.error(request, result['error'])

    return redirect('admin:mailings_mailing_changelist')


def home(request):
    now = timezone.now()

    # Пытаемся взять данные из кеша
    stats = cache.get('home_stats')
    print("🔍 КЕШ:", stats)
    if stats is None:
        # Пересчитываем статусы
        for mailing in Mailing.objects.all():
            mailing.update_status()

        stats = {
            'total_mailings': Mailing.objects.count(),
            'active_mailings': Mailing.objects.filter(
                start_time__lte=now,
                end_time__gte=now,
                status=Mailing.STATUS_STARTED
            ).count(),
            'unique_recipients': Client.objects.count(),
        }
        # Сохраняем в кеш на 15 минут
        cache.set('home_stats', stats, 60 * 15)

    return render(request, 'home.html', stats)


@login_required
def mailing_stats(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка доступа: владелец или менеджер
    if request.user.role != 'manager' and mailing.owner != request.user:
        messages.error(request, 'У вас нет доступа к этой статистике.')
        return redirect('home')

    # Считаем статистику
    attempts = mailing.attempts.all()
    total_sent = attempts.count()
    successful = attempts.filter(status=MailingAttempt.STATUS_SUCCESS).count()
    failed = attempts.filter(status=MailingAttempt.STATUS_FAILED).count()

    context = {
        'mailing': mailing,
        'total_sent': total_sent,
        'successful': successful,
        'failed': failed,
    }
    return render(request, 'mailings/stats.html', context)
