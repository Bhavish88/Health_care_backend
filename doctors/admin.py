from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialization', 'email', 'phone', 'experience_years', 'created_at')
    list_filter = ('specialization', 'experience_years')
    search_fields = ('name', 'specialization', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
