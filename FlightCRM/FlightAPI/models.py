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
    card_number = models.CharField(max_length=19)
    card_expiry_month = models.IntegerField()
    card_expiry_year = models.IntegerField()
    cvv = models.IntegerField()
    cardholder_name = models.CharField(max_length=100)

    def __str__(self):
        return self.cardholder_name
    
    def get_card_type(self):
        """
        Determine the card type based on the card number's IIN and length.
        Returns the card type as a string or 'Unknown' if it doesn't match any known type.
        """
        # Clean the card number to ensure it's numeric
        card_number = ''.join(filter(str.isdigit, self.card_number))
        if not card_number:
            return "Invalid"

        length = len(card_number)

        # VISA: Starts with 4, length 13, 16, or 19
        if card_number.startswith('4'):
            if length in [13, 16, 19]:
                return "VISA"
            return "Invalid"

        # MasterCard: Starts with 51-55 or 2221-2720, length 16
        if length == 16:
            if card_number.startswith(('51', '52', '53', '54', '55')):
                return "MasterCard"
            first_four = int(card_number[:4])
            if 2221 <= first_four <= 2720:
                return "MasterCard"

        # American Express: Starts with 34 or 37, length 15
        if card_number.startswith(('34', '37')) and length == 15:
            return "American Express"

        # Discover: Starts with 6011, 644-649, or 65, length 16 or 19
        if length in [16, 19]:
            if card_number.startswith(('6011', '65')):
                return "Discover"
            if card_number.startswith(('644', '645', '646', '647', '648', '649')):
                return "Discover"

        return "Unknown"

    def is_valid_luhn(self):
        """
        Validate the card number using the Luhn algorithm.
        Returns True if valid, False otherwise.
        """
        # Clean the card number to ensure it's numeric
        card_number = ''.join(filter(str.isdigit, self.card_number))
        if not card_number:
            return False

        digits = [int(d) for d in card_number]
        checksum = 0
        is_even = False

        # Start from the rightmost digit and move left
        for d in digits[::-1]:
            if is_even:
                d *= 2
                if d > 9:
                    d -= 9
            checksum += d
            is_even = not is_even

        return checksum % 10 == 0

    def clean(self):
        # Clean the card number to ensure it's numeric
        card_number = ''.join(filter(str.isdigit, self.card_number))
        if not card_number:
            raise ValidationError(_('Card number must contain only digits.'))
        self.card_number = card_number  # Update the card number to the cleaned version

        # Get the card type
        card_type = self.get_card_type()
        length = len(self.card_number)

        # Validate card number length based on card type
        if card_type == "American Express" and length != 15:
            raise ValidationError(_('American Express card numbers must be exactly 15 digits long.'))
        elif card_type in ["VISA", "Discover"] and length not in [13, 16, 19]:
            raise ValidationError(_('VISA and Discover card numbers must be 13, 16, or 19 digits long.'))
        elif card_type == "MasterCard" and length != 16:
            raise ValidationError(_('MasterCard numbers must be exactly 16 digits long.'))
        elif card_type in ["Unknown", "Invalid"]:
            raise ValidationError(_('Card type is not supported or invalid.'))

        # Validate Luhn algorithm
        if not self.is_valid_luhn():
            raise ValidationError(_('Card number fails Luhn validation.'))

        # Validate CVV length based on card type
        cvv_length = len(str(self.cvv))
        if card_type == "American Express" and cvv_length != 4:
            raise ValidationError(_('American Express CVV must be exactly 4 digits long.'))
        elif card_type in ["VISA", "MasterCard", "Discover"] and cvv_length != 3:
            raise ValidationError(_('VISA, MasterCard, and Discover CVV must be exactly 3 digits long.'))

        # Validate card expiry year format
        if len(str(self.card_expiry_year)) != 4:
            raise ValidationError(_('Card expiry year must be a 4-digit number (e.g., 2024, 2030).'))

        # Validate card expiry month
        if self.card_expiry_month < 1 or self.card_expiry_month > 12:
            raise ValidationError(_('Card expiry month must be between 1 and 12.'))

        # Validate card expiry date
        current_year = datetime.now().year
        current_month = datetime.now().month
        if self.card_expiry_year < current_year or (self.card_expiry_year == current_year and self.card_expiry_month < current_month):
            raise ValidationError(_('Card expiry date must be in the future.'))

        # Validate postal code length
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
    return_arrival_date = models.DateTimeField(blank=True, null=True, verbose_name="Flight Informations")
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
    customer_approval_datetime = models.DateTimeField(verbose_name="Authenticated At",blank=True,null=True)
    customer_ip = models.CharField(max_length=50,verbose_name="Customer IP",blank=True,null=True)
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