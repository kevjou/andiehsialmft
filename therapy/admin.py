from django.contrib import admin
from .models import AppointmentRequest, FAQ


@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'surname', 'email', 'created_at', 'is_responded']
    list_filter = ['is_responded', 'created_at']
    search_fields = ['name', 'surname', 'email']
    readonly_fields = ['created_at']
    list_editable = ['is_responded']
    ordering = ['-created_at']

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'surname', 'email')
        }),
        ('Appointment Details', {
            'fields': ('reason', 'is_responded')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']
    ordering = ['order']