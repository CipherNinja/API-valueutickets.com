from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date
from ckeditor.fields import RichTextField

class Airport(models.Model):
    city = models.CharField(max_length=255)
    airport_name = models.CharField(max_length=255) 
    faa = models.CharField(max_length=3, blank=True, null=True)
    iata = models.CharField(max_length=3, blank=True, null=True)
    icao = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return self.airport_name


class Customer(models.Model):
    phone_number = models.CharField(max_length=15,blank=False)
    email = models.EmailField(blank=False)
    name = models.CharField(max_length=255,blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "Flight Booking"


class Passenger(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    # Ticket Information
    airline_confirmation_number = models.CharField(max_length=300,blank=True,null=True)
    e_ticket_number = models.CharField(max_length=300, unique=True,blank=True,null=True)

    def __str__(self):
        # Fetch bookings through the Passenger's related Customer
        booking_ids = self.customer.bookings.values_list('booking_id', flat=True)
        if booking_ids:
            booking_id_str = ', '.join(booking_ids)
        else:
            booking_id_str = 'NA'
        return f"{booking_id_str} - {self.first_name} {self.last_name}"

    def get_age(self):
        today = date.today()
        age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        if age < 1:
            months = (today.year - self.dob.year) * 12 + today.month - self.dob.month
            if today.day < self.dob.day:
                months -= 1
            return f"{months} months"
        return f"{age} years"


class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    card_number = models.CharField(max_length=16)
    card_expiry_month = models.IntegerField()
    card_expiry_year = models.IntegerField()
    cvv = models.IntegerField()
    cardholder_name = models.CharField(max_length=100)

    def __str__(self):
        return self.cardholder_name

    def clean(self):
        # Validate card number length
        if len(self.card_number) != 16:
            raise ValidationError(_('Card number must be exactly 16 digits long.'))
        
        # Validate card expiry year format
        if len(str(self.card_expiry_year)) != 4:
            raise ValidationError(_('Card expiry year must be a 4-digit number Example: 2024, 2030, etc.'))
        
        # Validate card expiry month
        if self.card_expiry_month < 1 or self.card_expiry_month > 12:
            raise ValidationError(_('Card expiry month must be between 1 and 12.'))
        
        # Validate card expiry date
        current_year = datetime.now().year
        current_month = datetime.now().month
        if self.card_expiry_year < current_year or (self.card_expiry_year == current_year and self.card_expiry_month < current_month):
            raise ValidationError(_('Card expiry date must be in the future.'))
        
        # Validate CVV length
        if len(str(self.cvv)) not in [3, 4]:
            raise ValidationError(_('CVV must be either 3 or 4 digits long.'))
        
        # Validate postal code length (you can adjust this based on specific country's format)
        if len(self.postal_code) < 5 or len(self.postal_code) > 10:
            raise ValidationError(_('Postal code must be between 5 and 10 characters long.'))

    def save(self, *args, **kwargs):
        self.clean()
        super(Payment, self).save(*args, **kwargs)


class FlightBooking(models.Model):
    STATUS_CHOICES = [
        ('send flight information mail', 'Send Flight Information Mail'),
        ('send ticket confirmed mail', 'Send Ticket Confirmed Mail'),
        ('send ticket cancelled mail', 'Send Ticket Cancelled Mail'),
        ('Send Authorization Mail', 'Send Authorization Mail'),
        ('booking completed ticket not sent', 'Booking Completed Ticket Not Sent'),
        ('booking incompleted email not sent', 'Booking incomplete email don"t Sent'),
        ('refunded', 'Refunded'),
        ('rebooked', 'Rebooked'),
        ('booking failed', 'Booking Failed'),
    ]
    booking_id = models.CharField(max_length=12, unique=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    flight_name = models.CharField(max_length=200,blank=True, null=True)
    departure_iata = models.CharField(max_length=4, blank=True, null=True)
    arrival_iata = models.CharField(max_length=4, blank=True, null=True)
    departure_date = models.DateTimeField(blank=True, null=True)
    arrival_date = models.DateTimeField(blank=True, null=True)
    return_departure_iata = models.CharField(max_length=4, blank=True, null=True)
    return_arrival_iata = models.CharField(max_length=4, blank=True, null=True)
    return_departure_date = models.DateTimeField(blank=True, null=True)
    return_arrival_date = models.DateTimeField(blank=True, null=True)
    pnr_decoded_data = RichTextField(blank=True, help_text="Paste the PNR decoded data here")
    flight_cancellation_protection = models.BooleanField(default=False)
    sms_support = models.BooleanField(default=False)
    baggage_protection = models.BooleanField(default=False)
    premium_support = models.BooleanField(default=False)
    total_refund_protection = models.BooleanField(default=False)
    payble_amount = models.FloatField(verbose_name="Total Cost", null=True, blank=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user", default=1)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, verbose_name="Email Status", default='send flight information mail')
    customer_approval_status = models.CharField(max_length=20, choices=[('approved', 'Approved'), ('denied', 'Denied'), ("na", "NA")], default='na')
    customer_approval_datetime = models.DateTimeField(verbose_name="Authenticated At")
    net_mco = models.CharField(max_length=100,blank=True,verbose_name="Net MCO")
    mco = models.CharField(max_length=100,blank=True,verbose_name="MCO")
    issuance_fee = models.CharField(max_length=100,blank=True,verbose_name="Issuance Fees")
    ticket_cost = models.CharField(max_length=100,blank=True,verbose_name="Ticket Fees")

    def __str__(self):
        return f"{self.booking_id}"



class AgentFeedback(models.Model):
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name='agent_feedbacks'
    )
    agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='feedbacks_given'
    )
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.agent.username if self.agent else 'Unknown'} for {self.customer.email} on {self.created_at}"

    class Meta:
        verbose_name = "Agent Feedback"
        verbose_name_plural = "Agent Feedbacks"
        ordering = ['-created_at']  # Latest feedback first