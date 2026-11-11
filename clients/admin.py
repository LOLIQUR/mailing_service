from django.contrib import admin
from .models import Client

admin.site.has_permission = lambda request: request.user.is_active and request.user.is_staff

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'owner')
    search_fields = ('email', 'full_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'manager':
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
