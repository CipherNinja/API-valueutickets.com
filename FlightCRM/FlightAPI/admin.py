# from django.contrib import admin
# from .models import Customer, Passenger, Payment, FlightBooking, SendTicket, Airport
# from django import forms
# from datetime import date
# from django.contrib import admin
# from django.contrib.admin.models import LogEntry
# from datetime import timedelta
# from django.utils.timezone import now
# from django.utils.html import format_html
# from .signals import send_ticket_confirmation
# from .GeneratePDF.Flightpdf import export_to_excel


# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ('phone_number', 'email', 'date', 'get_booking_ids')
#     search_fields = ('phone_number', 'email', 'date', 'bookings__booking_id')

#     def get_booking_ids(self, obj):
#         bookings = obj.bookings.all()
#         return ', '.join([booking.booking_id for booking in bookings])
#     get_booking_ids.short_description = 'Booking IDs'

# @admin.register(Passenger)
# class PassengerAdmin(admin.ModelAdmin):
#     list_display = ('get_booking_ids', 'first_name', 'middle_name', 'last_name', 'dob', 'gender', 'customer', 'get_age')
#     list_filter = ('gender', 'dob', 'flights__booking_id')
#     search_fields = ('first_name', 'last_name', 'customer__phone_number', 'customer__email', 'flights__booking_id')
#     autocomplete_fields = ('customer',)

#     def get_booking_ids(self, obj):
#         bookings = obj.flights.all()
#         if bookings:
#             return ', '.join([booking.booking_id for booking in bookings])
#         return 'NA'
#     get_booking_ids.short_description = 'Booking IDs'

#     def get_age(self, obj):
#         today = date.today()
#         age = today.year - obj.dob.year - ((today.month, today.day) < (obj.dob.month, obj.dob.day))
#         if age < 1:
#             months = (today.year - obj.dob.year) * 12 + today.month - obj.dob.month
#             if today.day < obj.dob.day:
#                 months -= 1
#             return f"{months} months"
#         return f"{age} years"
#     get_age.short_description = 'Age'

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_superuser or request.user.groups.filter(name='flightapi_admin').exists():
#             return qs
#         visible_bookings = FlightBooking.objects.filter(agent=request.user)
#         visible_booking_ids = visible_bookings.values_list('id', flat=True)
#         return qs.filter(flights__id__in=visible_booking_ids)


# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('get_booking_ids', 'cardholder_name', 'get_masked_card_number', 'cvv', 'card_expiry_month', 'card_expiry_year', 'customer', 'country', 'state', 'city', 'address_line1', 'address_line2')
#     list_filter = ('card_expiry_year', 'country', 'city', 'flightbooking__booking_id')
#     search_fields = ('cardholder_name', 'customer__phone_number', 'customer__email', 'flightbooking__booking_id')
#     autocomplete_fields = ('customer',)

#     def get_masked_card_number(self, obj):
#         if obj:
#             return '********' + obj.card_number[-4:]
#     get_masked_card_number.short_description = 'Card Number'

#     def get_booking_ids(self, obj):
#         bookings = FlightBooking.objects.filter(payment=obj)
#         return ', '.join([booking.booking_id for booking in bookings])
#     get_booking_ids.short_description = 'Booking IDs'

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
#             visible_bookings = FlightBooking.objects.filter(agent=request.user)
#             visible_booking_ids = visible_bookings.values_list('id', flat=True)
#             qs = qs.filter(flightbooking__id__in=visible_booking_ids)
#         return qs

#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         if obj and not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
#             original_card_number = obj.card_number
#             masked_card_number = '********' + original_card_number[-4:]
#             form.base_fields['card_number'].initial = masked_card_number
#             form.base_fields['card_number'].widget.attrs['readonly'] = True
#         return form

#     def save_model(self, request, obj, form, change):
#         if not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
#             if 'card_number' in form.initial:
#                 obj.card_number = form.initial['card_number'].replace('********', '')
#         super().save_model(request, obj, form, change)



# @admin.register(FlightBooking)
# class FlightBookingAdmin(admin.ModelAdmin):
#     list_display = (
#         'booking_id', 'customer', 'get_passenger_names', 'payment', 'flight_name', 
#         'departure_iata', 'arrival_iata', 'departure_date', 'arrival_date',
#         'return_departure_iata', 'return_arrival_iata', 'return_departure_date', 'return_arrival_date', 
#         'flight_cancellation_protection', 'sms_support', 'baggage_protection', 
#         'premium_support', 'total_refund_protection', 'payble_amount', 'agent', 'status', 'customer_approval_status',
#     )
#     actions = [export_to_excel]
#     list_filter = (
#         'booking_id', 'customer', 'payment__cardholder_name', 'departure_iata', 'arrival_iata', 'status', 'customer_approval_status',
#         'return_departure_iata', 'return_arrival_iata',
#     )
#     search_fields = ('booking_id',)

#     filter_horizontal = ('passengers',)
#     autocomplete_fields = ('customer',)
#     readonly_fields = ('booking_id', 'customer_approval_status')

#     fieldsets = (
#         ('Flight Information', {
#             'fields': (
#                 'flight_name', 'departure_iata', 'arrival_iata', 'departure_date', 'arrival_date',
#                 'return_departure_iata', 'return_arrival_iata', 'return_departure_date', 'return_arrival_date', 'customer_approval_status',
#             )
#         }),
#         ('Customer Information', {
#             'fields': (
#                 'customer', 'passengers', 'agent'
#             )
#         }),
#         ('Payment Information', {
#             'fields': (
#                 'payment', 'payble_amount','booking_id', 'flight_cancellation_protection', 'sms_support', 'baggage_protection', 'premium_support', 
#                 'total_refund_protection', 'status',
#             )
#         }),
        
#     )

#     def get_passenger_names(self, obj):
#         passenger_links = []
#         for p in obj.passengers.all():
#             url = f"/admin/FlightAPI/passenger/{p.id}/change/"
#             link = format_html('<a href="{}">{}</a>', url, f"{p.first_name} {p.middle_name} {p.last_name}".replace("  ", " "))
#             passenger_links.append(link)
#         return format_html(', '.join(passenger_links))
#     get_passenger_names.short_description = 'Passengers'

#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         if obj and not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
#             for field_name in form.base_fields:
#                 form.base_fields[field_name].disabled = True
#         return form

#     def get_readonly_fields(self, request, obj=None):
#         if obj and not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
#             return self.readonly_fields + tuple(field.name for field in self.model._meta.fields)
#         return self.readonly_fields

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_superuser or request.user.groups.filter(name='flightapi_admin').exists():
#             return qs
#         return qs.filter(agent=request.user)

#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         extra_context = extra_context or {}
#         if object_id and not request.user.is_superuser and not request.user.groups.filter(name='flightapi_admin').exists():
#             extra_context['show_save'] = False
#             extra_context['show_save_and_continue'] = False
#             extra_context['show_save_and_add_another'] = False
#         return super().change_view(request, object_id, form_url, extra_context=extra_context)

#     def add_view(self, request, form_url='', extra_context=None):
#         extra_context = extra_context or {}
#         return super().add_view(request, form_url, extra_context=extra_context)
    


# LogEntry._meta.verbose_name = ("Track Staff Activity")
# LogEntry._meta.verbose_name_plural = ("Track Staff Activities")

# class LogEntryAdmin(admin.ModelAdmin):
#     list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message')
#     search_fields = ('object_repr', 'change_message')

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         today = now().date()
#         yesterday = today - timedelta(days=1)
#         return queryset.filter(action_time__date__in=[today, yesterday])

#     def has_add_permission(self, request):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False

#     def has_delete_permission(self, request, obj=None):
#         return False

# admin.site.register(LogEntry, LogEntryAdmin)


# '''
# PNR - Airline Confirmation Number,
# Airline Info,
# Ticket Number,


# '''


from django.contrib import admin
from .models import Customer, Passenger, Payment, FlightBooking, Airport


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('city', 'airport_name', 'iata', 'icao', 'faa')
    search_fields = ('city', 'airport_name', 'iata', 'icao', 'faa')



# Passenger Inline for Customer
class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 1


# Payment Inline for Customer
class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 1


class FlightBookingInline(admin.StackedInline):
    model = FlightBooking
    extra = 0  # Prevent extra blank entries
    show_change_link = True
    readonly_fields = ('customer_approval_status', 'booking_id')
    fields = (
         'agent', 'status', 'customer_approval_status','booking_id', 'pnr_decoded_data', 'flight_name', 'arrival_iata', 'departure_iata', 'arrival_date', 'departure_date','return_arrival_iata', 'return_departure_iata', 'return_arrival_date', 'return_departure_date',
        'flight_cancellation_protection', 'sms_support', 'baggage_protection',
        'premium_support', 'total_refund_protection', 'payble_amount',
        'net_mco', 'mco', 'issuance_fee', 'ticket_cost',
    )


    def get_max_num(self, request, obj=None, **kwargs):
        return 1  # Ensure only one FlightBooking instance per Customer
    
    class Media:
        css = {
            'all': ('custom.css',),  # Path to your custom CSS file
        }

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [PassengerInline, PaymentInline, FlightBookingInline]
    list_display = (
        'get_booking_id',
        'name', 
        'email', 
        'phone_number', 
        'get_payable_amount', 
        'get_net_mco', 
        'get_mco', 
        'get_issuance_fee', 
        'get_ticket_cost', 
        'get_booking_status', 
        'get_customer_approval_status', 
        'get_agent', 
        'get_passenger_count', 
        'get_payment_count',
        'date'
    )
    search_fields = ('name', 'email', 'phone_number', 'bookings__booking_id', 'bookings__flight_name')
    list_filter = ('date',)

    def get_booking_id(self, obj):
        bookings = obj.bookings.all()
        return ", ".join([b.booking_id for b in bookings if b.booking_id]) if bookings.exists() else "N/A"
    get_booking_id.short_description = 'Booking ID'

    def get_payable_amount(self, obj):
        bookings = obj.bookings.all()
        return ", ".join([f"{b.payble_amount}$" for b in bookings if b.payble_amount]) if bookings.exists() else "N/A"
    get_payable_amount.short_description = 'Payable Amount'

    def get_net_mco(self, obj):
        bookings = obj.bookings.all()
        return ", ".join([f"{b.net_mco}$" for b in bookings if b.net_mco]) if bookings.exists() else "N/A"
    get_net_mco.short_description = 'Net MCO'

    def get_mco(self, obj):
        bookings = obj.bookings.all()
        return ", ".join([f"{b.mco}$" for b in bookings if b.mco]) if bookings.exists() else "N/A"
    get_mco.short_description = 'MCO'

    def get_issuance_fee(self, obj):
        bookings = obj.bookings.all()
        return ", ".join([f"{b.issuance_fee}$" for b in bookings if b.issuance_fee]) if bookings.exists() else "N/A"
    get_issuance_fee.short_description = 'Issuance Fee'

    def get_ticket_cost(self, obj):
        bookings = obj.bookings.all()
        return ", ".join([f"{b.ticket_cost}$" for b in bookings if b.ticket_cost]) if bookings.exists() else "N/A"
    get_ticket_cost.short_description = 'Ticket Cost'

    def get_customer_approval_status(self, obj):
        bookings = obj.bookings.all()
        return ", ".join([b.customer_approval_status for b in bookings if b.customer_approval_status]) if bookings.exists() else "N/A"
    get_customer_approval_status.short_description = 'Customer Approval'

    def get_agent(self, obj):
        bookings = obj.bookings.all()
        return ", ".join([b.agent.username for b in bookings if b.agent]) if bookings.exists() else "N/A"
    get_agent.short_description = 'Assigned Agent'

    def get_passenger_count(self, obj):
        return obj.passengers.count()
    get_passenger_count.short_description = 'Passenger Count'

    def get_payment_count(self, obj):
        return obj.payments.count()
    get_payment_count.short_description = 'Payment Count'

    def get_booking_status(self, obj):
        bookings = obj.bookings.all()
        if not bookings.exists():
            return "N/A"
        
        # Map statuses to Confirmed/Cancelled/Pending
        status_map = {
            'send ticket confirmed mail': 'Confirmed',
            'booking completed ticket not sent': 'Confirmed',
            'send ticket cancelled mail': 'Cancelled',
            'refunded': 'Cancelled',
        }
        
        # Get the simplified status for each booking
        simplified_statuses = []
        for booking in bookings:
            simplified_status = status_map.get(booking.status, 'Pending')  # Default to Pending if not in map
            simplified_statuses.append(simplified_status)
        
        return ", ".join(simplified_statuses)
    get_booking_status.short_description = 'Status'


    class Media:
        js = ('custom.js',)


