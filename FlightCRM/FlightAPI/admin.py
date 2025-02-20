from django.contrib import admin
from .models import Customer, Passenger, Payment, FlightBooking, Ticket, Airport
from django import forms
from datetime import date
from rangefilter.filters import DateRangeFilter
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from datetime import timedelta
from django.utils.timezone import now
from django.utils.html import format_html


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'email', 'date', 'get_booking_ids')
    search_fields = ('phone_number', 'email', 'date', 'bookings__booking_id')

    def get_booking_ids(self, obj):
        bookings = obj.bookings.all()
        return ', '.join([booking.booking_id for booking in bookings])
    get_booking_ids.short_description = 'Booking IDs'

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('get_booking_ids', 'first_name', 'middle_name', 'last_name', 'dob', 'gender', 'customer', 'get_age')
    list_filter = ('gender', 'dob', 'flights__booking_id')
    search_fields = ('first_name', 'last_name', 'customer__phone_number', 'customer__email', 'flights__booking_id')
    autocomplete_fields = ('customer',)

    def get_booking_ids(self, obj):
        bookings = obj.flights.all()
        return ', '.join([booking.booking_id for booking in bookings])
    get_booking_ids.short_description = 'Booking IDs'

    def get_age(self, obj):
        today = date.today()
        age = today.year - obj.dob.year - ((today.month, today.day) < (obj.dob.month, obj.dob.day))
        if age < 1:
            months = (today.year - obj.dob.year) * 12 + today.month - obj.dob.month
            if today.day < obj.dob.day:
                months -= 1
            return f"{months} months"
        return f"{age} years"
    get_age.short_description = 'Age'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        visible_bookings = FlightBooking.objects.all()
        if not request.user.is_superuser:
            visible_bookings = visible_bookings.filter(agent=request.user)
        visible_booking_ids = visible_bookings.values_list('id', flat=True)
        return qs.filter(flights__id__in=visible_booking_ids)

from django.contrib import admin
from .models import Payment, FlightBooking

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('get_booking_ids', 'cardholder_name', 'get_masked_card_number', 'cvv', 'card_expiry_month', 'card_expiry_year', 'customer', 'country', 'state', 'city', 'address_line1', 'address_line2')
    list_filter = ('card_expiry_year', 'country', 'city', 'flightbooking__booking_id')
    search_fields = ('cardholder_name', 'customer__phone_number', 'customer__email', 'flightbooking__booking_id')
    autocomplete_fields = ('customer',)

    def get_masked_card_number(self, obj):
        if obj:
            return '********' + obj.card_number[-4:]
    get_masked_card_number.short_description = 'Card Number'

    def get_booking_ids(self, obj):
        bookings = FlightBooking.objects.filter(payment=obj)
        return ', '.join([booking.booking_id for booking in bookings])
    get_booking_ids.short_description = 'Booking IDs'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            visible_bookings = FlightBooking.objects.filter(agent=request.user)
            visible_booking_ids = visible_bookings.values_list('id', flat=True)
            qs = qs.filter(flightbooking__id__in=visible_booking_ids)
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
            if 'card_number' in form.initial:
                obj.card_number = form.initial['card_number'].replace('********', '')
        super().save_model(request, obj, form, change)



@admin.register(FlightBooking)
class FlightBookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id', 'customer', 'get_passenger_names', 'payment', 'flight_name', 
        'departure_iata', 'arrival_iata', 'departure_date', 'arrival_date', 
        'flight_cancellation_protection', 'sms_support', 'baggage_protection', 
        'premium_support', 'total_refund_protection', 'payble_amount', 'agent', 'status', 'customer_approval_status',
    )
    list_filter = (
        'booking_id', 'customer', 'payment__cardholder_name', 'departure_iata', 'arrival_iata', 'status', 'customer_approval_status',
        # ('departure_date', DateRangeFilter)
    )
    search_fields = ('booking_id',)

    filter_horizontal = ('passengers',)
    autocomplete_fields = ('customer',)
    readonly_fields = ('booking_id', 'customer_approval_status')

    def get_passenger_names(self, obj):
        passenger_links = []
        for p in obj.passengers.all():
            url = f"/admin/FlightAPI/passenger/{p.id}/change/"
            link = format_html('<a href="{}">{}</a>', url, f"{p.first_name} {p.middle_name} {p.last_name}".replace("  ", " "))
            passenger_links.append(link)
        return format_html(', '.join(passenger_links))
    get_passenger_names.short_description = 'Passengers'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and not request.user.is_superuser:
            for field_name in form.base_fields:
                form.base_fields[field_name].disabled = True
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return self.readonly_fields + tuple(field.name for field in self.model._meta.fields)
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(agent=request.user)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id and not request.user.is_superuser:
            extra_context['show_save'] = False
            extra_context['show_save_and_continue'] = False
            extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        return super().add_view(request, form_url, extra_context=extra_context)

        


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


LogEntry._meta.verbose_name = ("Track Staff Activity")
LogEntry._meta.verbose_name_plural = ("Track Staff Activities")

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