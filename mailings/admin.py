from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import Mailing, MailingAttempt
from .views import mailing_stats


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'status', 'owner', 'view_stats')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'manager':
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def view_stats(self, obj):
        return f'<a href="/mailings/stats/{obj.pk}/" target="_blank">Посмотреть</a>'

    view_stats.allow_tags = True
    view_stats.short_description = 'Статистика'
