from django.contrib import admin
from .models import Customer, Passenger, Payment, FlightBooking, SendTicket, Airport
from django import forms
from datetime import date
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from datetime import timedelta
from django.utils.timezone import now
from django.utils.html import format_html
from .signals import send_ticket_confirmation
from .GeneratePDF.Flightpdf import export_to_excel

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('city', 'airport_name', 'iata', 'icao', 'faa')
    search_fields = ('city', 'airport_name', 'iata', 'icao', 'faa')


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
        if bookings:
            return ', '.join([booking.booking_id for booking in bookings])
        return 'NA'
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
        if request.user.is_superuser or request.user.groups.filter(name='flightapi_admin').exists():
            return qs
        visible_bookings = FlightBooking.objects.filter(agent=request.user)
        visible_booking_ids = visible_bookings.values_list('id', flat=True)
        return qs.filter(flights__id__in=visible_booking_ids)


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
        if not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
            visible_bookings = FlightBooking.objects.filter(agent=request.user)
            visible_booking_ids = visible_bookings.values_list('id', flat=True)
            qs = qs.filter(flightbooking__id__in=visible_booking_ids)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
            original_card_number = obj.card_number
            masked_card_number = '********' + original_card_number[-4:]
            form.base_fields['card_number'].initial = masked_card_number
            form.base_fields['card_number'].widget.attrs['readonly'] = True
        return form

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
            if 'card_number' in form.initial:
                obj.card_number = form.initial['card_number'].replace('********', '')
        super().save_model(request, obj, form, change)



@admin.register(FlightBooking)
class FlightBookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id', 'customer', 'get_passenger_names', 'payment', 'flight_name', 
        'departure_iata', 'arrival_iata', 'departure_date', 'arrival_date',
        'return_departure_iata', 'return_arrival_iata', 'return_departure_date', 'return_arrival_date', 
        'flight_cancellation_protection', 'sms_support', 'baggage_protection', 
        'premium_support', 'total_refund_protection', 'payble_amount', 'agent', 'status', 'customer_approval_status',
    )
    actions = [export_to_excel]
    list_filter = (
        'booking_id', 'customer', 'payment__cardholder_name', 'departure_iata', 'arrival_iata', 'status', 'customer_approval_status',
        'return_departure_iata', 'return_arrival_iata',
    )
    search_fields = ('booking_id',)

    filter_horizontal = ('passengers',)
    autocomplete_fields = ('customer',)
    readonly_fields = ('booking_id', 'customer_approval_status')

    fieldsets = (
        ('Flight Information', {
            'fields': (
                'flight_name', 'departure_iata', 'arrival_iata', 'departure_date', 'arrival_date',
                'return_departure_iata', 'return_arrival_iata', 'return_departure_date', 'return_arrival_date', 'customer_approval_status',
            )
        }),
        ('Customer Information', {
            'fields': (
                'customer', 'passengers', 'agent'
            )
        }),
        ('Payment Information', {
            'fields': (
                'payment', 'payble_amount','booking_id', 'flight_cancellation_protection', 'sms_support', 'baggage_protection', 'premium_support', 
                'total_refund_protection', 'status',
            )
        }),
        
    )

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
        if obj and not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
            for field_name in form.base_fields:
                form.base_fields[field_name].disabled = True
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
            return self.readonly_fields + tuple(field.name for field in self.model._meta.fields)
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='flightapi_admin').exists():
            return qs
        return qs.filter(agent=request.user)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id and not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
            extra_context['show_save'] = False
            extra_context['show_save_and_continue'] = False
            extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        return super().add_view(request, form_url, extra_context=extra_context)
    

class TicketAdmin(admin.ModelAdmin):
    list_display = ('get_booking_id', 'get_passenger_full_name', 'get_cardholder_name', 'get_customer_email', 'get_customer_phone_number', 'get_booking_status', 'airline_confirmation_number', 'e_ticket_number')
    search_fields = ('booking__booking_id', 'e_ticket_number', 'airline_confirmation_number')
    list_filter = ('booking__status', 'booking__customer__email', 'booking__payment__cardholder_name')
    def get_booking_id(self, obj):
        return obj.booking.booking_id
    get_booking_id.short_description = 'Booking ID'
    
    def get_passenger_full_name(self, obj):
        return f"{obj.passenger.first_name} {obj.passenger.last_name}"
    get_passenger_full_name.short_description = 'Passenger'
    
    def get_cardholder_name(self, obj):
        return obj.booking.payment.cardholder_name
    get_cardholder_name.short_description = 'Cardholder Name'
    
    def get_customer_email(self, obj):
        return obj.booking.customer.email
    get_customer_email.short_description = 'Customer Email'
    
    def get_customer_phone_number(self, obj):
        return obj.booking.customer.phone_number
    get_customer_phone_number.short_description = 'Customer Phone Number'
    
    def get_booking_status(self, obj):
        return obj.booking.status
    get_booking_status.short_description = 'Booking Status'

admin.site.register(SendTicket, TicketAdmin)



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


'''
PNR - Airline Confirmation Number,
Airline Info,
Ticket Number,


'''