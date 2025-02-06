from django.contrib import admin
from .models import Customer, Passenger, Payment, FlightBooking, Ticket, Airport
from django import forms
from rangefilter.filters import DateRangeFilter

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
    list_display = ('cardholder_name', 'card_number', 'cvv', 'card_expiry_month', 'card_expiry_year', 'customer')
    list_filter = ('card_expiry_year', 'country', 'city')
    search_fields = ('cardholder_name', 'card_number', 'customer__phone_number', 'customer__email')
    autocomplete_fields = ('customer',)

@admin.register(FlightBooking)
class FlightBookingAdmin(admin.ModelAdmin):
    list_display = (
        'customer', 'payment', 'flight_name', 'departure_iata', 'arrival_iata', 
        'departure_date', 'arrival_date', 'flight_cancellation_protection', 
        'sms_support', 'baggage_protection', 'premium_support', 'total_refund_protection', 'payble_amount'
    )
    list_filter = (
        'flight_cancellation_protection','baggage_protection', 
        'departure_iata', 'arrival_iata',
        ('departure_date', DateRangeFilter)
    )
    search_fields = (
        'customer__phone_number', 'customer__email', 'payment__cardholder_name', 
        'flight_name', 'departure_iata', 'arrival_iata'
    )
    filter_horizontal = ('passengers',)
    autocomplete_fields = ('customer',)



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
