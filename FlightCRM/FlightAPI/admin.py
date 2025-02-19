from django.contrib import admin
from .models import Customer, Passenger, Payment, FlightBooking, Ticket, Airport
from django import forms
from rangefilter.filters import DateRangeFilter
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from datetime import timedelta
from django.utils.timezone import now
from django.utils.html import format_html


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'email', 'date')
    search_fields = ('phone_number', 'email', 'date')

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'middle_name', 'last_name', 'dob', 'gender', 'customer')
    list_filter = ('gender', 'dob')
    search_fields = ('first_name', 'last_name', 'customer__phone_number', 'customer__email')
    autocomplete_fields = ('customer',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('cardholder_name', 'get_masked_card_number', 'cvv', 'card_expiry_month', 'card_expiry_year', 'customer', 'country', 'state', 'city', 'address_line1', 'address_line2')
    list_filter = ('card_expiry_year', 'country', 'city')
    search_fields = ('cardholder_name', 'get_masked_card_number', 'customer__phone_number', 'customer__email')
    autocomplete_fields = ('customer',)

    def get_masked_card_number(self, obj):
        request = self.request
        if request.user.is_superuser:
            return obj.card_number
        else:
            return '********' + obj.card_number[-4:]

    get_masked_card_number.short_description = 'Card Number'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        self.request = request
        return qs

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and not request.user.is_superuser:
            original_card_number = obj.card_number
            masked_card_number = '********' + original_card_number[-4:]
            form.base_fields['card_number'].initial = masked_card_number
            form.base_fields['card_number'].widget.attrs['readonly'] = True
        return form

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.card_number = form.initial['card_number'].replace('********', '')
        super().save_model(request, obj, form, change)



@admin.register(FlightBooking)
class FlightBookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id','customer', 'get_passenger_names', 'payment', 'flight_name', 
        'departure_iata', 'arrival_iata', 'departure_date', 'arrival_date', 
        'flight_cancellation_protection', 'sms_support', 'baggage_protection', 
        'premium_support', 'total_refund_protection', 'payble_amount','agent','status','customer_approval_status',
    )
    list_filter = (
        'customer','payment__cardholder_name','departure_iata', 'arrival_iata','status','customer_approval_status',
        # ('departure_date', DateRangeFilter)
    )

    filter_horizontal = ('passengers',)
    autocomplete_fields = ('customer',)
    readonly_fields = ('booking_id','customer_approval_status')

    def get_passenger_names(self, obj):
        return ', '.join([f"{p.first_name} {p.middle_name} {p.last_name}".replace("  ", " ") for p in obj.passengers.all()])
    get_passenger_names.short_description = 'Passengers'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['agent'].disabled = True
        return form
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(agent=request.user)


class TicketAdminForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TicketAdminForm, self).__init__(*args, **kwargs)
        self.help_texts = {
            'note': "This feature allows you to send tickets via email in a professional format. Ensure that the information is accurate as it represents official communication."
        }

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    form = TicketAdminForm
    fieldsets = (
        (None, {
            'fields': ('customer', 'pdf_file', 'message'),
        }),
        ('Important Notice', {
            'fields': (),
            'description': 'This feature allows you to send tickets via email in a professional format. Ensure that the information is accurate as it represents official communication.',
        }),
    )


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message')
    search_fields = ('object_repr', 'change_message')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        today = now().date()
        yesterday = today - timedelta(days=1)
        return queryset.filter(action_time__date__in=[today, yesterday])

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(LogEntry, LogEntryAdmin)