from django.contrib import admin
from .models import Certificate, CertificateTemplate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'certificate_id', 'issued_date', 'is_valid']
    list_filter = ['is_valid', 'issued_date', 'course']
    search_fields = ['student__username', 'course__title', 'certificate_id']
    readonly_fields = ['certificate_id']

@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'created']
    list_filter = ['is_default', 'created']
    search_fields = ['name', 'title_text', 'body_text']
