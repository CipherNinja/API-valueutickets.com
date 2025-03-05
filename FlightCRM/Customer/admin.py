from django.contrib import admin
from .models import ContactUs

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'country', 'submitted_at')
    list_filter = ('country', 'submitted_at')
    search_fields = ('name', 'email', 'phone', 'message','country')
    readonly_fields = ('submitted_at',)


admin.site.register(ContactUs, ContactUsAdmin)
