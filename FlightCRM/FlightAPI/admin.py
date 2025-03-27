from django.contrib import admin
from .models import Customer, Passenger, Payment, FlightBooking, Airport, AgentFeedback
from django.contrib.auth.models import User
from django.utils.html import format_html


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
    readonly_fields = ('customer_approval_status', 'customer_approval_datetime', 'booking_id')
    fields = (
         'agent', 'status', 'customer_approval_status','customer_approval_datetime','booking_id', 'pnr_decoded_data', 'flight_name', 'arrival_iata', 'departure_iata', 'arrival_date', 'departure_date','return_arrival_iata', 'return_departure_iata', 'return_arrival_date', 'return_departure_date',
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

# AgentFeedback Inline for Customer
class AgentFeedbackInline(admin.TabularInline):
    model = AgentFeedback
    extra = 1
    readonly_fields = ('created_at_display', 'agent_display')
    fields = ('agent_display', 'note', 'created_at_display')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-created_at')

    def save_model(self, request, obj, form, change):
        print(f"Current user: {request.user}, Authenticated: {request.user.is_authenticated}")
        if not change:  # Only set agent on creation
            if request.user.is_authenticated:
                obj.agent = request.user
                print(f"Setting agent to {request.user.username} (ID: {request.user.id}) for feedback on {obj.customer.email}")
            else:
                print("User is not authenticated! Cannot set agent.")
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "agent":
            kwargs["initial"] = request.user
            kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Store the request for use in agent_display
        self.request = request

        # Dynamically set readonly fields for each form in the formset
        class DynamicFormset(formset):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for form in self.forms:
                    # Get the AgentFeedback instance for this form
                    if form.instance and form.instance.pk:
                        # If the agent of this feedback is not the current user, make the note readonly
                        if form.instance.agent != request.user:
                            form.fields['note'].widget.attrs['readonly'] = True
                            form.fields['note'].widget.attrs['class'] = 'readonly-note'
        return DynamicFormset

    def agent_display(self, obj):
        obj = AgentFeedback.objects.get(pk=obj.pk)
        # Add a class to indicate if this is the current user's feedback
        is_current_user = obj.agent == self.request.user if obj.agent else False
        agent_name = obj.agent.username if obj.agent else "Unknown Agent"
        return format_html('<span class="{}">{}</span>', 'current-user' if is_current_user else 'other-user', agent_name)
    agent_display.short_description = "Agent"

    def created_at_display(self, obj):
        return obj.created_at.strftime('%B %d, %Y, %I:%M %p').replace('AM', 'a.m.').replace('PM', 'p.m.')
    created_at_display.short_description = "Created at"

    class Media:
        css = {
            'all': ('custom.css',),
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
        'get_customer_ip',
        'get_customer_approval_status',
        'get_customer_approval_datetime',
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

    def get_customer_approval_datetime(self, obj):
        bookings = obj.bookings.all()
        return ", ".join([
            b.customer_approval_datetime.strftime('%Y-%m-%d %H:%M:%S') 
            for b in bookings if b.customer_approval_datetime
        ]) if bookings.exists() and any(b.customer_approval_datetime for b in bookings) else "Not authenticated"
    get_customer_approval_datetime.short_description = 'Authenticated At'

    def get_customer_ip(self, obj):
        bookings = obj.bookings.all()
        return ", ".join([b.customer_ip for b in bookings if b.customer_ip]) if bookings.exists() else "N/A"
    get_customer_ip.short_description = 'Customer IP'

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


